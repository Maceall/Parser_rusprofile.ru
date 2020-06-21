import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'rusprofile'
    
    id = sqlalchemy.Column(sqlalchemy.INTEGER, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.Text)
    ogrn = sqlalchemy.Column(sqlalchemy.BIGINT)
    okpo = sqlalchemy.Column(sqlalchemy.BIGINT)
    status = sqlalchemy.Column(sqlalchemy.Text)
    reg_date = sqlalchemy.Column(sqlalchemy.DATE)
    capital = sqlalchemy.Column(sqlalchemy.BIGINT)
    
   
def connect_db():
    engine = sqlalchemy.create_engine('mysql+pymysql://test:rewyseT1!@localhost/rusprofile?charset=utf8')
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    session = Session()
    
    return session


connect = connect_db()


def wr_data(name,ogrn,okpo,status,reg_date,capital):
    '''
    Создаем объекты класса User для записи в БД из созданных списков 
    по искомым данным орг-ии
    '''

    # если данных нет в БД, то счетчик id начинаем с ноля 
    if connect.query(User).order_by(-User.id).first() == None:
        for i in range(len(name)):
            user = User(
                id = i + 1,
                name = name[i],
                ogrn = ogrn[i],
                okpo = okpo[i],
                status = status[i],
                reg_date = reg_date[i],
                capital = capital[i]
                )
            connect.add(user)

    # если данные уже имеются в БД, увеличиваем счетчик на существующий id + 1 
    else: 
        id = connect.query(User).order_by(-User.id).first().id
        for i in range(len(name)):
            user = User(
                id = i + 1 + id,
                name = name[i],
                ogrn = ogrn[i],
                okpo = okpo[i],
                status = status[i],
                reg_date = reg_date[i],
                capital = capital[i]
            )
            connect.add(user)
    
    connect.commit()