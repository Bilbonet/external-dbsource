# Copyright 2021 Jesus Ramiro <jesus@bilbonet.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class BaseExternalDbsource(models.Model):
    """ It provides logic for update an external data source
        with an SQL sentence.
        You can pass parameters in a dictionary
    """
    _inherit = 'base.external.dbsource'

    def commit(self, query=None, execute_params=None):
        """ Executes update query and returns a number of rows updated.

            "execute_params" can be a dict of values, that can be referenced
            in the SQL statement using "%(key)s" or, in the case of Oracle,
            ":key".
            Example:
                query = "SELECT * FROM mytable WHERE city = %(city)s AND
                            date > %(dt)s"
                execute_params   = {
                    'city': 'Lisbon',
                    'dt': datetime.datetime(2000, 12, 31),
                }
        """
        method = self._get_adapter_method('update')
        number = method(query, execute_params)

        return number

    def _commit_generic(self, query, params):
        with self.connection_open() as connection:
            cur = connection.cursor()
            number = cur.execute(query, params).rowcount
            cur.commit()

            return number
