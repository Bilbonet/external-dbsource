# Copyright <2011> <Daniel Reis, Maxime Chambreuil, Savoir-faire Linux>
# Copyright 2016 LasLabs Inc.
# Copyright 2021 Jesus Ramiro <jesus@bilbonet.net>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': 'External Database Source - ODBC',
    'version': '14.0.1.0.1',
    'category': 'Tools',
    'author': "Daniel Reis, "
              "LasLabs, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/Bilbonet/external-dbsource',
    'license': 'LGPL-3',
    'depends': ['base_external_dbsource'],
     'external_dependencies': {
        'python': ['pyodbc'],
     },
    'demo': ['demo/base_external_dbsource.xml'],
    'installable': True,
}
