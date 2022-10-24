# Copyright 2021 Jesus Ramiro <jesus@bilbonet.net>
# Copyright <2011> <Daniel Reis>
# Copyright <2016> <Liu Jianyun>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Import data from external data sources.',
    'version': '14.0.1.0.0',
    'category': 'Tools',
    'author': "Jesus Ramiro, Liu Jianyun, Daniel Reis, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/Bilbonet/server-tools',
    "license": "AGPL-3",
    'images': [
        'images/snapshot1.png',
        'images/snapshot2.png',
    ],
    'depends': [
        'base',
        'base_external_dbsource',
    ],
    'data': [
        'views/base_external_import_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/base_external_import_demo.xml',
    ],
    'test': [],
    'installable': True,
    'active': False,
}
