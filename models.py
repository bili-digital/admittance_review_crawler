from main import db
import datetime

class BaseMixin(object):
    @classmethod
    def create(cls, **kw):
        kw['created_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        kw['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        obj = cls(**kw)
        db.session.add(obj)
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