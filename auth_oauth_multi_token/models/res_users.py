# Copyright 2016 Florent de Labarre
# Copyright 2017 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import uuid

from odoo import api, fields, models, exceptions

from odoo.addons import base

base.models.res_users.USER_PRIVATE_FIELDS. \
    append('oauth_master_uuid')


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _generate_oauth_master_uuid(self):
        return uuid.uuid4().hex

    oauth_access_token_ids = fields.One2many(
        comodel_name='auth.oauth.multi.token',
        inverse_name='user_id',
        string='OAuth tokens',
        copy=False,
        readonly=True,
        groups='base.group_system'
    )
    oauth_access_max_token = fields.Integer(
        string='Max number of simultaneous connections',
        default=10,
        required=True
    )
    oauth_master_uuid = fields.Char(
        string='Master UUID',
        copy=False,
        readonly=True,
        required=True,
        default=lambda self: self._generate_oauth_master_uuid(),
    )

    @property
    def multi_token_model(self):
        return self.env['auth.oauth.multi.token']

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        """Override to handle sign-in with multi token."""
        res = super()._auth_oauth_signin(
            provider, validation, params)

        oauth_uid = validation['user_id']
        # Lookup for user by oauth uid and provider
        user = self.search([
            ('oauth_uid', '=', oauth_uid),
            ('oauth_provider_id', '=', provider)]
        )
        if not user:
            raise exceptions.AccessDenied()
        user.ensure_one()
        # user found and unique: create a token
        self.multi_token_model.create({
            'user_id': user.id,
            'oauth_access_token': params['access_token'],
            'active_token': True,
        })

        try:
            if validation['@odata.context'] == "https://graph.microsoft.com/v1.0/$metadata#users/$entity":   
                
                email = validation['userPrincipalName']
                name = validation['displayName']

                user = self.env['res.users'].search([('id', '=', user.id)])
                
                if user.name != name:
                
                    user.write({
                        'share': False, 
                        'name': name, 
                        'login': email,
                        'email': email,
                        'active': True,
                        'company_id': 1 
                    })

                # Busca empleado con el mismo email registrado en odoo y en active directory
                id_e = self.env['hr.employee'].search([('work_email', 'ilike', validation['userPrincipalName'])],
                                                      limit=1).id
                # Si el empleado existe
                if id_e:
                    # Busca que el empleado tenga el ya asignado algun usuario
                    id_u = self.env['hr.employee'].search([('id', '=', id_e), ('user_id', '=', user.id)], limit=1).id
                    # Si empleado no tiene al usuario relacionado
                    if id_u is False:
                        # Relaciona al empleado con el usuario
                        employee = self.env['hr.employee'].search([('id', '=', id_e)])
                        employee.write({'user_id': user.id})

                        # Busca empleado con el mismo email registrado en odoo y en active directory
                        id_p = self.env['res.partner'].search([('email', '=', validation['userPrincipalName'])],
                                                              limit=1).id
                        # Si el empleado existe
                        if id_p:
                            partner = self.env['res.partner'].search([('id', '=', id_p)])
                            partner.write({'parent_id': 1, 'company_id': 1, 'employee': 'true'})

                            group_e = self.env.ref('base.group_portal', False)
                            group_e.write({'users': [(3, user.id)]})

                            group_u = self.env.ref('base.group_user', False)
                            group_u.write({'users': [(4, user.id)]})

        except Exception as e:
            print("Mensaje: ", e)
        return res

    def action_oauth_clear_token(self):
        """Inactivate current user tokens."""
        self.mapped('oauth_access_token_ids')._oauth_clear_token()
        for res in self:
            res.oauth_master_uuid = self._generate_oauth_master_uuid()

    @api.model
    def _check_credentials(self, password):
        """Override to check credentials against multi tokens."""
        try:
            return super()._check_credentials(password)
        except exceptions.AccessDenied:
            res = self.multi_token_model.sudo().search([
                ('user_id', '=', self.env.uid),
                ('oauth_access_token', '=', password),
                ('active_token', '=', True),
            ])
            if not res:
                raise

    def _get_session_token_fields(self):
        res = super()._get_session_token_fields()
        res.remove('oauth_access_token')
        return res | {'oauth_master_uuid'}
