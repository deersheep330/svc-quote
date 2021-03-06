from sqlalchemy import Column, String, Date, Integer, func

from ..db import Base

class TwseOverSold(Base):

    __tablename__ = 'twse_over_sold'

    symbol = Column(String(16), nullable=False, primary_key=True)
    date = Column(Date, nullable=False, primary_key=True, server_default=func.sysdate())
    quantity = Column(Integer, nullable=False)

    def __repr__(self):
        return str([getattr(self, c.name, None) for c in self.__table__.c])
