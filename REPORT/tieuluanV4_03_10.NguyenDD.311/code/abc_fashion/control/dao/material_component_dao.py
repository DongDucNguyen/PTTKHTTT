# Generated from the Visual Paradigm model "Design" (package abc_fashion.control.dao.material_component_dao) -- do not edit the signatures.
from __future__ import annotations


from abc_fashion.control.dao.dao import DAO
from abc_fashion.model.catalogue import tblMaterialComponent, tblStyle


class MaterialComponentDAO(DAO):
    """MaterialComponentDAO -- layer abc_fashion.control.dao.
    Holds (model layer): tblMaterialComponent
    """

    def get_material_by_style(self, style: tblStyle):
        raise NotImplementedError

    def save_material(self, style: tblStyle, materials: list[tblMaterialComponent]):
        raise NotImplementedError
