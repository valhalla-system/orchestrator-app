from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

client_image_table = Table(
    "client_image",
    Base.metadata,
    Column("client_mac", String, ForeignKey("clients.mac_address")),
    Column("image_id", Integer, ForeignKey("vm_images.image_id"))
)

class Client(Base):
    __tablename__ = "clients"
    mac_address = Column(String, primary_key=True)
    ip_address = Column(String)
    hostname = Column(String)
    client_version = Column(String)
    vm_list_on_machine = relationship(
        "VMImages",
        secondary = client_image_table,
        back_populates = "vm_images"
    )
    
    def has_vm_installed(self, vm_object):
        for vm in self.vm_list_on_machine:
            if vm.image_hash == vm_object.image_hash:
                return True
        return False

class VMImage(Base):
    __tablename__ = "vm_images"
    image_id = Column(Integer, primary_key=True)
    image_name = Column(String)
    image_file = Column(String)
    image_version = Column(String)
    image_hash = Column(String)
    clients = relationship(
        "Clients",
        secondary = client_image_table,
        back_populates = "clients"
    )