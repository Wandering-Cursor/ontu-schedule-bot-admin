from main.models.base import BaseModel


class AbstractScheduleEntity(BaseModel):
    async def get_short_id(
        self,
        max_length: int = 8,
    ) -> str:
        """Recursively finds the smallest most specific identifier for the schedule entity."""
        if max_length < 1:
            raise ValueError("max_length must be at least 1")

        id_string = str(self.uuid)
        current_length = 1
        short_id = id_string[:current_length]

        while current_length < max_length:
            short_id = id_string[:current_length]
            if await self.__class__.objects.filter(uuid__startswith=short_id).acount() == 1:
                return short_id
            current_length += 1

        return short_id

    class Meta(BaseModel.Meta):
        abstract = True
