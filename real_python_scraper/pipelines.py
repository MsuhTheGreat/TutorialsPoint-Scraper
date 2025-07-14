# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class RealPythonPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Strip Whitespaces
        field_names = adapter.field_names()
        for field_name in field_names:
            value = adapter.get(field_name)
            if isinstance(value, str):
                adapter[field_name] = value.strip()
        
        # Get correct publish date
        date_lst = adapter.get("publish_date")
        adapter["publish_date"] = date_lst[-1].strip("\n").strip()

        # Convert List of contents to a string
        list_of_contents = adapter.get("list_of_contents")
        value = "\n".join(list_of_contents)
        adapter["list_of_contents"] = value

        # Convert tags to a string
        tags_lst = adapter.get("tags")
        if len(tags_lst) == 1:
            value = tags_lst[0]
        else:
            value = ", ".join(tags_lst)
        adapter["tags"] = value

        return item
