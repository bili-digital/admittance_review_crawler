from server import db
import datetime

class BaseMixin(object):
    @classmethod
    def create(cls, **kw):
        kw['created_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        kw['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        obj = cls(**kw)
        r = db.session.add(obj)
        db.session.commit()

class ConsumerDebt(BaseMixin, db.Model):
    __tablename__ = 'py_consumer_debts'
    # 設定 primary_key
    id = db.Column(db.Integer, primary_key=True)
    court = db.Column(db.String(45))
    title = db.Column(db.String(45))
    date = db.Column(db.DateTime)
    content = db.Column(db.String(45))
    tenant_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self, court, title, date, content, tenant_id, created_at="", updated_at=""):
        self.court = court
        self.title = title
        self.date = date
        self.content = content
        self.tenant_id = tenant_id
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return '<ConsumerDebt %r>' % self.content
class CriminalRecord(BaseMixin, db.Model):
    __tablename__ = 'py_criminal_records'
    # 設定 primary_key
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(45))
    judge_date = db.Column(db.DateTime)
    reason = db.Column(db.String(45))
    tenant_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self, title, judge_date, reason, tenant_id, created_at="", updated_at=""):
        self.title = title
        self.judge_date = judge_date
        self.reason = reason
        self.tenant_id = tenant_id
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return '<CriminalRecord %r>' % self.reason

class CurrentWanted(BaseMixin, db.Model):
    __tablename__ = 'py_current_wanteds'
    # 設定 primary_key
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45))
    id_number = db.Column(db.String(45))
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self, name, id_number, created_at="", updated_at=""):
        self.name = name
        self.id_number = id_number
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return '<CurrentWanted %r>' % self.name

class Domestic(BaseMixin, db.Model):
    __tablename__ = 'py_domestic'
    # 設定 primary_key
    id = db.Column(db.Integer, primary_key=True)
    court = db.Column(db.String(45))
    title = db.Column(db.String(45))
    post_date = db.Column(db.DateTime)
    publish_date = db.Column(db.DateTime)
    content = db.Column(db.String(45))
    tenant_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self, court, title, post_date, publish_date, content, tenant_id, created_at="", updated_at=""):
        self.court = court
        self.title = title
        self.post_date = post_date
        self.publish_date = publish_date
        self.content = content
        self.tenant_id = tenant_id
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return '<Domestic %r>' % self.title

class FuelPenaltyBasic(BaseMixin, db.Model):
    __tablename__ = 'py_fuel_penalty_basic'
    # 設定 primary_key
    id = db.Column(db.Integer, primary_key=True)
    transportation = db.Column(db.String(45))
    car_number = db.Column(db.String(45))
    period = db.Column(db.String(45))
    should_paid_date = db.Column(db.DateTime)
    supervisory_department = db.Column(db.String(45))
    amount = db.Column(db.Integer)
    comment = db.Column(db.String(45))
    tenant_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self, transportation, car_number, period, should_paid_date, supervisory_department,amount,comment,tenant_id, created_at="", updated_at=""):
        self.transportation = transportation
        self.car_number = car_number
        self.period = period
        self.should_paid_date = should_paid_date
        self.supervisory_department = supervisory_department
        self.amount = amount
        self.comment = comment
        self.tenant_id = tenant_id
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return '<FuelPenaltyBasic %r>' % self.title
class FuelPenaltyExpire(BaseMixin, db.Model):
    __tablename__ = 'py_fuel_penalty_expired'
    # 設定 primary_key
    id = db.Column(db.Integer, primary_key=True)
    transportation = db.Column(db.String(45))
    car_number = db.Column(db.String(45))
    bill_number = db.Column(db.String(45))
    should_paid_date = db.Column(db.DateTime)
    supervisory_department = db.Column(db.String(45))
    amount = db.Column(db.Integer)
    comment = db.Column(db.String(45))
    tenant_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self, transportation, car_number, bill_number, should_paid_date, supervisory_department,amount,comment,tenant_id, created_at="", updated_at=""):
        self.transportation = transportation
        self.car_number = car_number
        self.bill_number = bill_number
        self.should_paid_date = should_paid_date
        self.supervisory_department = supervisory_department
        self.amount = amount
        self.comment = comment
        self.tenant_id = tenant_id
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return '<FuelPenaltyExpire %r>' % self.transportation

class TrafficPenalty(BaseMixin, db.Model):
    __tablename__ = 'py_trafic_penalty'
    # 設定 primary_key
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(45))
    violation_date = db.Column(db.DateTime)
    should_paid_date = db.Column(db.DateTime)
    amount = db.Column(db.Integer)
    tenant_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self, content, violation_date, should_paid_date, amount,tenant_id, created_at="", updated_at=""):
        self.content = content
        self.violation_date = violation_date
        self.should_paid_date = should_paid_date
        self.amount = amount
        self.tenant_id = tenant_id
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return '<TrafficPenalty %r>' % self.content

class Wanted(BaseMixin, db.Model):
    __tablename__ = 'py_wanteds'
    # 設定 primary_key
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(45))
    tenant_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self, status,tenant_id, created_at="", updated_at=""):
        self.status = status
        self.tenant_id = tenant_id
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return '<Wanted %r>' % self.status


class Criminal(BaseMixin, db.Model):
    __tablename__ = 'py_criminals'
    # 設定 primary_key
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(45))
    tenant_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self, status,tenant_id, created_at="", updated_at=""):
        self.status = status
        self.tenant_id = tenant_id
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return '<Criminal %r>' % self.status