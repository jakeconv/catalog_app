import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


# Users: keep track of registered email addresses
class User(Base):
    __tablename__ = 'user'
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    # The picture is collected but not used in
    # this version of the app.
    # (Future feature)
    picture = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Return data in a JSON friendly format
        return {
            'name': self.name,
            'id': self.id,
            }


class CatalogItem(Base):
    __tablename__ = 'catalog_item'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    # The user who created the category
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    # The category this catalog item belongs to
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    # Use a timestamp to show the most recent items
    date_created = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def serialize(self):
        # Return data in a JSON friendly format
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            }

engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
