# Copyright <2021> Jesus Ramiro <jesus@bilbonet.net>
# Copyright <2016> <Liu Jianyun>
# Copyright <2011> <Daniel Reis>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import sys
import logging
from datetime import datetime
from odoo import models, fields
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
_loglvl = _logger.getEffectiveLevel()


class Log(models.Model):
    _name = "base.external.import.log"
    _description = 'Log'
    _rec_name = 'import_id'

    import_id = fields.Many2one('base.external.import.task', string='Import Task', readonly=True)
    start_run = fields.Datetime(string='Time started', readonly=True)
    last_run = fields.Datetime(string='Time ended', readonly=True)
    last_record_count = fields.Integer(string='Last record count', readonly=True)
    last_error_count = fields.Integer(string='Last error count', readonly=True)
    last_warn_count = fields.Integer(string='Last warning count', readonly=True)
    last_log = fields.Text(string='Last run log', readonly=True)


class Task(models.Model):
    _name = "base.external.import.task"
    _description = 'External Import Task'
    _order = 'exec_order'

    name = fields.Char(required=True, string='Name', size=64)
    enabled = fields.Boolean(string='Execution enabled', default=True)
    dbsource_id = fields.Many2one('base.external.dbsource', string='Database source', required=True)
    sql_source = fields.Text(string='SQL', required=True,
        help='Column names must be valid "import_data" columns.')
    model_target = fields.Many2one('ir.model', string='Target object', required=True, ondelete='cascade')
    exec_order = fields.Integer(string='Execution order', default=10,
        help="Defines the order to perform the import")
    last_sync = fields.Datetime(string='Last sync time',
        help="Datetime for the last successful sync. \nLater changes \
             on the source may not be replicated on the destination"
    )
    start_run = fields.Datetime(string='Time started', readonly=True, copy=False)
    last_run = fields.Datetime(string='Time ended', readonly=True, copy=False)
    last_record_count = fields.Integer(string='Last record count', readonly=True, copy=False)
    last_error_count = fields.Integer(string='Last error count', readonly=True, copy=False)
    last_warn_count = fields.Integer(string='Last warning count', readonly=True, copy=False)
    last_log = fields.Text(string='Last run log', readonly=True, copy=False)
    log_enabled = fields.Boolean(string='Log enabled', default=True)

    def _import_data(self, flds, data, model_obj, log):
        """ Import data and create records.
        :param
            flds: List of fields to import
            data: The data to import in each field
            model_obj: Object model where record will be created
            table_obj: Object task import definition
            log: In this param writes data of each record importation
        :returns
            False or id of the record created
        """

        def append_to_log(log, level, obj_id='', msg='', rel_id=''):
            if '_id_' in obj_id:
                obj_id = ('.'.join(obj_id.split('_')[:-2]) + ': ' +
                          obj_id.split('_')[-1])
            if ': .' in msg and not rel_id:
                rel_id = msg[msg.find(': .')+3:]
                if '_id_' in rel_id:
                    rel_id = ('.'.join(rel_id.split('_')[:-2]) +
                              ': ' + rel_id.split('_')[-1])
                    msg = msg[:msg.find(': .')]
            log['last_log'].append('%s|%s\t|%s\t|%s' % (level.ljust(5),
                                                        obj_id, rel_id, msg))

        _logger.debug(data)
        cols = list(flds)  # copy to avoid side effects
        errmsg = str()

        importmsg = dict()
        try:
            importmsg = model_obj.load(cols, [data])
        except:
            errmsg = str(sys.exc_info()[1])
        if errmsg:
            # Fail
            append_to_log(log, 'ERROR', data, errmsg)
            log['last_error_count'] += 1
            return False

        # Check the import model returned message
        if not importmsg['ids']:
            message = [i['message'] for i in importmsg['messages']
                       if 'message' in i]
            _logger.debug(message)
            append_to_log(log, 'WARN', data, message)
            log['last_warn_count'] += 1
            return False

        return int(importmsg['ids'][0])

    def import_run(self, ids=None, param_values=None):
        """
        :param
            ids: id or List of ids of import tasks that you want to run
            param_values: A list of Values for the SQL params in the query
        :returns False or a list with two lists inside [external_ids, odoo_ids]
            external_ids: List of ExternalIDS of records created
            odoo:ids: List ids of records created
        """

        run_ids = None
        if isinstance(ids, int):
            run_ids = [ids]
        elif isinstance(ids, list):
            run_ids = ids
        else:
            run_ids = self.ids

        if run_ids:
            actions = self.search(
                [('id', 'in', run_ids),
                 ('enabled', '=', True)], order='exec_order')
        else:
            actions = self.search([('enabled', '=', True)], order='exec_order')

        # Consider each task:
        for action_ref in actions:
            obj = self.browse(action_ref['id'])
            if not obj.enabled:
                continue

            db_model = \
                self.env['base.external.dbsource'].browse(obj.dbsource_id.id)

            _logger.setLevel(logging.DEBUG or _loglvl)
            _logger.debug('Importing %s...' % obj.name)

            model_name = obj.model_target.model
            model_obj = self.env.get(model_name)

            # now() microseconds are stripped to avoid problem with SQL smalldate
            log = {'start_run': datetime.now().replace(microsecond=0),
                   'last_run': None,
                   'last_record_count': 0,
                   'last_error_count': 0,
                   'last_warn_count': 0,
                   'last_log': list()}
            obj.write(log)

            # Prepare params and last_sync date param
            params = list()
            if isinstance(param_values, list):
                params = param_values
            if obj.last_sync:
                params.append(obj.last_sync)

            try:
                res = db_model.execute(obj.sql_source, params, metadata=True)
            except Exception:
                errmsg = str(sys.exc_info()[1])
                errmsg += '\n %s' % params
                raise ValidationError(errmsg)

            # Exclude columns titled "Id" and Add (xml_)"id" column
            cidx = ([i for i, x in enumerate(res['cols'])
                     if x.upper() != 'ID'])
            cols = ([x for i, x in enumerate(res['cols'])
                     if x.upper() != 'ID'] + ['id'])

            # Check all columns has name
            for i in cols:
                if not i:
                    raise ValidationError(
                        "review the query any of the columns hasn't name")

            # Prepare the internal XML-ID in column "id"
            def build_xmlid(row_id):
                # Replace dots "." by "-" in XML-ID dots are not allowed
                row_id = str(row_id).replace('.', '-')
                # Prepare prefix
                xml_prefix = '__import__.' + model_name.replace('.', '_') + '_'
                return xml_prefix + row_id

            external_ids = list()
            odoo_ids = list()
            # Import each row
            for row in res['rows']:
                # Build data row;
                # import only columns present in the "cols" list
                data = list()
                for i in cidx:
                    v = row[i]
                    if isinstance(v, str):
                        v = v.strip()
                    if isinstance(v, datetime):
                        v = v.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    data.append(v)
                data.append(build_xmlid(row[0]).strip())

                # Import the row;
                log['last_record_count'] += 1
                imported_id = self._import_data(cols, data, model_obj, log)
                if log['last_record_count'] % 500 == 0:
                    _logger.info('...%s rows processed...'
                                 % (log['last_record_count']))
                if imported_id:
                    external_ids.append(row[0])
                    odoo_ids.append(imported_id)


            # Finished importing all rows
            # If no errors and the task has last_sync, we update last_sync date
            if not (log['last_error_count'] or log['last_warn_count'])\
                    and obj.last_sync:
                log['last_sync'] = log['start_run']

            # Write logs
            level = logging.DEBUG
            if log['last_warn_count']:
                level = logging.WARN
            if log['last_error_count']:
                level = logging.ERROR
            _logger.log(level,
                        'Imported %s , %d rows, %d errors, %d warnings.' %
                        (model_name, log['last_record_count'],
                         log['last_error_count'],
                         log['last_warn_count']))

            # Write run log in the task, either if the log option is active or not
            if log['last_log']:
                log['last_log'].insert(
                    0,
                    'LEVEL | == Line == | == Relationship == | == Message =='
                    )
            log.update({
                'last_log': '\n'.join(log['last_log']),
                'last_run': datetime.now().replace(microsecond=0)
            })
            obj.write(log)

            # Save log if the option is enabled
            if obj.log_enabled:
                import_logs = {
                    'import_id': obj.id,
                    'start_run': log['start_run'],
                    'last_run': log['last_run'],
                    'last_record_count': log['last_record_count'],
                    'last_error_count': log['last_error_count'],
                    'last_warn_count': log['last_warn_count'],
                    'last_log': log['last_log']
                }
                self.env['base.external.import.log'].create(import_logs)

        # Finished
        _logger.debug('Import job FINISHED.')
        if external_ids and odoo_ids:
            return [external_ids, odoo_ids]
        else:
            return False

    def import_schedule(self):
        cron_obj = self.env['ir.cron']
        new_create = cron_obj.create({
            'name': self.name,
            'model_id': self.env.ref(
                'base_external_import.model_base_external_import_task').id,
            'state': 'code',
            'code': 'model.import_run(%s)' % self.id,
            'user_id': self.env.ref('base.user_root').id,
            'interval_number': 24,
            'interval_type': 'hours',
            'numbercall': -1,
            'doall': False,
            'active': False
        })
        return {
            'name': 'External Data Import',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'ir.cron',
            'res_id': new_create.id,
            'type': 'ir.actions.act_window',
        }
