# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import Controller, request
from odoo.addons import base

class ApiJsonrpc(http.Controller):
    @http.route('/api/auth', type='json', auth='none', methods=["POST"])
    def authenticate(self, db, login, password):        
        request.session.authenticate(db, login, password)
        return request.env['ir.http'].session_info()
    
    @http.route('/api/get_contacts', type='json', auth='user')
    def get_contacts(self):
        contact_rec = request.env['res.partner'].search([])
        contacts = []
        for rec in contact_rec:
            vals = {
                'id': rec.id,
                'name': rec.name
            }
            contacts.append(vals)
        data = {'status': 200, 'response': contacts, 'message': 'Success'}
        return data
    
    @http.route('/api/create_company', type='json', auth='user')
    def create_company(self, **rec):

        global response, id_country, id_state

        if request.jsonrequest:
            if rec['name']:

                if rec['country']:
                    id_country = request.env['res.country'].search([('name', '=', rec['country'])], limit=1).id
                    if id_country is None:
                        id_country = ''

                if rec['state']:
                    id_state = request.env['res.country.state'].search([('name', '=', rec['state'])], limit=1).id
                    if id_state is None:
                        id_state = ''

                vals = {
                    'name': rec['name'],
                    'vat': rec['rfc'],
                    'website': rec['website'],
                    'street': rec['street'],
                    'street2': rec['street2'],
                    'zip': rec['zip'],
                    'city': rec['city'],
                    'country_id': id_country,
                    'state_id': id_state,
                    'email': rec['email'],
                    'phone': rec['phone'],
                    'mobile': rec['mobile'],
                    'is_company': 'true'
                }

                try:

                    # 1. Insert new Partner
                    new_contact = request.env['res.partner'].sudo().create(vals)

                    # 2. Search Tag
                    id_category = request.env['res.partner.category'].search([('name', '=', 'Asociada')], limit=1).id

                    # 3. If tag exist
                    if id_category > 0:
                        request.cr.execute("""insert into res_partner_res_partner_category_rel(category_id,partner_id) 
                                           values(""" + str(id_category) + """,""" + str(new_contact.id) + """)""")
                    # 4. If not exist else create tag
                    else:
                        category = {'name': 'Asociada'}
                        request.env['res.partner.category'].sudo().create(category)

                    response = {'success': True, 'message': 'Company successfully created', 'ID': new_contact.id}

                except Exception as e:
                    response = {'success': True, 'message': e}

            else:
                response = {'success': True, 'message': 'Incomplete values'}

        args = response
        return args

    @http.route('/api/create_contact', type='json', auth='user')
    def create_contact(self, **rec):

        global response, id_company, id_country, id_state

        if request.jsonrequest:
            if rec['name']:
                
                if rec['company']:
                    id_company = request.env['res.partner'].search([('name', 'ilike', rec['company'])], limit=1).id
                    if id_company is False:
                        id_company = ''

                if rec['country']:
                    id_country = request.env['res.country'].search([('name', '=', rec['country'])], limit=1).id
                    if id_country is None:
                        id_country = ''

                if rec['state']:
                    id_state = request.env['res.country.state'].search([('name', '=', rec['state'])], limit=1).id
                    if id_state is None:
                        id_state = ''

                vals = {
                    'name': rec['name'],
                    'vat': rec['rfc'],
                    'website': rec['website'],
                    'street': rec['street'],
                    'street2': rec['street2'],
                    'zip': rec['zip'],
                    'city': rec['city'],
                    'country_id': id_country,
                    'state_id': id_state,
                    'email': rec['email'],
                    'phone': rec['phone'],
                    'mobile': rec['mobile'],
                    'is_company': 'false',
                    'parent_id': id_company
                }

                try:

                    # 1. Insert new Contact
                    new_contact = request.env['res.partner'].sudo().create(vals)

                    # 2. Search Tag
                    id_category = request.env['res.partner.category'].search([('name', '=', 'Asociada')], limit=1).id

                    # 3. If category exist
                    if id_category > 0:
                        request.cr.execute("""insert into res_partner_res_partner_category_rel(category_id,partner_id) 
                                                   values(""" + str(id_category) + """,""" + str(
                            new_contact.id) + """)""")
                    # 4. If not exist else create tag
                    else:
                        category = {'name': 'Asociada'}
                        request.env['res.partner.category'].sudo().create(category)

                    response = {'success': True, 'message': 'Contact successfully created', 'ID': new_contact.id}

                except Exception as e:
                    response = {'success': True, 'message': e}

            else:
                response = {'success': True, 'message': 'Incomplete values'}

            args = response
            return args
        
    @http.route('/api/create_approval', type='json', auth='user')
    def create_approval(self, **rec):

        global response, id_company, id_category

        if request.jsonrequest:
            
            if rec['name']:
                
                id_category = request.env['approval.category'].search([('name', '=', 'Solicitud de Donativo')], limit=1).id
                
                if id_category > 0: 
                    
                    if rec['company']:
                        id_company = request.env['res.partner'].search([('name', 'ilike', rec['company'])], limit=1).id
                        if id_company is False:
                            id_company = ''
                    
                    user_id = request.env['res.users'].sudo().search([('login', '=', rec['approval'])], limit=1).id
                    
                    vals = {
                        'name': rec['name'],
                        'category_id': id_category,
                        'date': rec['date'],
                        'quantity': '1',
                        'partner_id': id_company,
                        'reference': rec['reference'],
                        'amount': rec['amount'],
                        'reason': rec['reason'],
                        'request_status': 'new',
                        'request_owner_id': user_id
                    }
                    
                    try:
                        
                        # 1. Create new Request
                        
                        new_request = request.env['approval.request'].sudo().create(vals)                    
                                        
                        # 2. Create new Approval
                         
                        request.env['approval.approver'].sudo().create({
                            'user_id': user_id,
                            'request_id': new_request.id,
                            'status': 'new'})
                    
                        # Send Email to Request Aproval
                        # mail_template = request.env['mail.template'].search([('name', 'like', 'Approval_Template')])
                        # mail_template.write({'email_to': rec['approval'],})
                        # mail_template.send_mail(user_id, force_send = True)

                        response = {'success': True, 'message': 'Success', 'ID': new_request.id}    
                    
                    except Exception as e:
                        print(e)
                        response = {'success': True, 'message': e}
                
                else:
                    response = {'success': True, 'message': 'We cant find the category, please create it and try again'}

            else:
                response = {'success': True, 'message': 'Incomplete values'}

            args = response
            return args   
        

                   