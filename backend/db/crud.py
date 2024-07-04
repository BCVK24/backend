from sqlalchemy import select, Select


class CRUD:
    @classmethod
    def get_by_id(cls, id: int) -> Select:
        query = (
            select(cls)
            .where(cls.id == id)
        )

        return query
