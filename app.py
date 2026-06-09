from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
import os

app = Flask(__name__)

@app.route('/')
def home():
    return {
        "project": "Interview Tracker API",
        "status": "Running"
    }

# DATABASE CONFIG
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# ==========================
# MODELS
# ==========================

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100))
    location = db.Column(db.String(100))

    applications = db.relationship(
        'Application',
        backref='company',
        cascade='all, delete'
    )

    def __init__(self, company_name, location):
        self.company_name = company_name
        self.location = location


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(100))
    applied_date = db.Column(db.String(50))
    status = db.Column(db.String(50))

    company_id = db.Column(
        db.Integer,
        db.ForeignKey('company.id')
    )

    def __init__(self, role, applied_date, status, company_id):
        self.role = role
        self.applied_date = applied_date
        self.status = status
        self.company_id = company_id


# ==========================
# SCHEMAS
# ==========================

class CompanySchema(ma.Schema):
    id = fields.Integer()
    company_name = fields.String()
    location = fields.String()


class ApplicationSchema(ma.Schema):
    id = fields.Integer()
    role = fields.String()
    applied_date = fields.String()
    status = fields.String()
    company_id = fields.Integer()


company_schema = CompanySchema()
companies_schema = CompanySchema(many=True)

application_schema = ApplicationSchema()
applications_schema = ApplicationSchema(many=True)

# ==========================
# COMPANY CRUD
# ==========================

@app.route('/company', methods=['POST'])
def add_company():
    company_name = request.json['company_name']
    location = request.json['location']

    company = Company(company_name, location)

    db.session.add(company)
    db.session.commit()

    return company_schema.jsonify(company)


@app.route('/company', methods=['GET'])
def get_companies():
    companies = Company.query.all()
    result = companies_schema.dump(companies)
    return jsonify(result)


@app.route('/company/<int:id>', methods=['GET'])
def get_company(id):
    company = Company.query.get(id)
    return company_schema.jsonify(company)


@app.route('/company/<int:id>', methods=['PUT'])
def update_company(id):
    company = Company.query.get(id)

    company.company_name = request.json['company_name']
    company.location = request.json['location']

    db.session.commit()

    return company_schema.jsonify(company)


@app.route('/company/<int:id>', methods=['DELETE'])
def delete_company(id):
    company = Company.query.get(id)

    db.session.delete(company)
    db.session.commit()

    return company_schema.jsonify(company)


# ==========================
# APPLICATION CRUD
# ==========================

@app.route('/application', methods=['POST'])
def add_application():

    role = request.json['role']
    applied_date = request.json['applied_date']
    status = request.json['status']
    company_id = request.json['company_id']

    application = Application(
        role,
        applied_date,
        status,
        company_id
    )

    db.session.add(application)
    db.session.commit()

    return application_schema.jsonify(application)


@app.route('/application', methods=['GET'])
def get_applications():
    applications = Application.query.all()
    result = applications_schema.dump(applications)
    return jsonify(result)


@app.route('/application/<int:id>', methods=['GET'])
def get_application(id):
    application = Application.query.get(id)
    return application_schema.jsonify(application)


@app.route('/application/<int:id>', methods=['PUT'])
def update_application(id):

    application = Application.query.get(id)

    application.role = request.json['role']
    application.applied_date = request.json['applied_date']
    application.status = request.json['status']
    application.company_id = request.json['company_id']

    db.session.commit()

    return application_schema.jsonify(application)


@app.route('/application/<int:id>', methods=['DELETE'])
def delete_application(id):

    application = Application.query.get(id)

    db.session.delete(application)
    db.session.commit()

    return application_schema.jsonify(application)


# ==========================
# DASHBOARD
# ==========================

@app.route('/dashboard', methods=['GET'])
def dashboard():

    total = Application.query.count()

    applied = Application.query.filter_by(
        status='Applied'
    ).count()

    assessment = Application.query.filter_by(
        status='Assessment'
    ).count()

    interview = Application.query.filter_by(
        status='Interview'
    ).count()

    selected = Application.query.filter_by(
        status='Selected'
    ).count()

    rejected = Application.query.filter_by(
        status='Rejected'
    ).count()

    return jsonify({
        "total_applications": total,
        "applied": applied,
        "assessment": assessment,
        "interview": interview,
        "selected": selected,
        "rejected": rejected
    })


# ==========================
# CREATE DATABASE
# ==========================

with app.app_context():
    db.create_all()



if __name__ == '__main__':
    app.run(debug=True)

