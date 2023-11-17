import asyncio
import csv
from typing import Any, Callable

import wx
import wx.grid as gridlib
from pubsub import pub

from app.database import get_tables_content, DataSource, db_dump, get_table_names
from app.extractor import CSVFileDataWriter


# model
class AsyncModel:
    """
    A model for asynchronous load.
    """
    def __init__(self, datasource):
        self.datasource = datasource

    async def fetch_table_names(self, schema_name: str):
        return get_table_names(self.datasource, schema_name)

    def fetch_tables_content(self, table_names: list[str]):
        return get_tables_content(self.datasource, table_names)


class GridTable(gridlib.GridTableBase):
    def __init__(self, model: AsyncModel):
        gridlib.GridTableBase.__init__(self)

        self.columns = ["", "Table name"]
        self.column_types = [gridlib.GRID_VALUE_BOOL, gridlib.GRID_VALUE_STRING]
        self.model = model
        self.data = []

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        number_cols = len(self.columns)
        return number_cols

    def GetColLabelValue(self, col):
        return self.columns[col]

    def IsEmptyCell(self, row, col):
        try:
            return not self.data[row][col]
        except IndexError:
            return True

    def GetValue(self, row, col):
        return self.data[row][col]

    def GetTypeName(self, row, col):
        return self.column_types[col]

    def CanGetValueAs(self, row, col, type_name):
        col_type = self.column_types[col].split(':')[0]
        if type_name == col_type:
            return True
        else:
            return False

    def CanSetValueAs(self, row, col, typeName):
        return self.CanGetValueAs(row, col, typeName)

    def SetValue(self, row, col, value):

        def inner_set_value():
            try:
                self.data[row][col] = value
            except IndexError:
                # add a new row
                self.data.append([False, ''])
                inner_set_value()
                self.notify_rows_appended()
        inner_set_value()

    def notify_rows_appended(self):
        msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED, 1)
        self.GetView().ProcessTableMessage(msg)


class Controller:

    def __init__(self, table: GridTable, loaded_hook: Callable[..., Any]):
        self.table = table
        self.hook = loaded_hook

    def table_names_loaded(self, table_names: list[str]):
        data = [[c0, c1] for c0, c1 in zip([False] * len(table_names), table_names)]
        for table_name in table_names:
            print(f'Table name: {table_name}')

        for i in range(len(data)):
            for j in range(self.table.GetNumberCols()):
                self.table.SetValue(i, j, data[i][j])

        self.hook("loading finished")

    def export_to_csv(self, tables_content: db_dump):
        def write_table_to_csv(table_name, columns, rows):
            self.hook(f"exporting {table_name}.csv")
            print(f"{table_name}\n\t{columns}\n", end="")
            for row in rows:
                print("\t{row}".format(**dict(row=row)))
                try:
                    writer = CSVFileDataWriter(f"{table_name}.csv", True)
                    writer.write([list(columns)] + [list(row) for row in list(rows)])
                    self.hook(f"exporting to {table_name}.csv finished")
                except csv.Error:
                    self.hook(f"exporting failed")

        for table_name, columns_and_rows in tables_content.items():
            columns, rows = columns_and_rows
            write_table_to_csv(table_name, columns, rows)

    def get_selected_table_names(self):
        return [row[1] for row in self.table.data if row[0]]

    async def load_table_names(self, schema_name: str, callback: Callable[..., Any]):
        pub.subscribe(callback, "table_names_loaded")
        self.hook("loading started")
        table_names = await self.table.model.fetch_table_names(schema_name)
        self.hook("loading finished")

        pub.sendMessage(topicName="table_names_loaded", table_names=table_names)

    async def load_and_fill_table_names(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.load_table_names(self.table.model.datasource.get_database(), self.table_names_loaded))

    async def load_table_content(self, table_names: list[str], callback: Callable[..., Any]):
        pub.subscribe(callback, "tables_content_loaded")
        self.hook("loading started")
        tables_content = self.table.model.fetch_tables_content(table_names)
        self.hook("loading finished")
        pub.sendMessage(topicName="tables_content_loaded", tables_content=tables_content)

    async def load_and_export_table_content(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.load_table_content(self.get_selected_table_names(), self.export_to_csv))


class GridView(gridlib.Grid):
    def __init__(self, parent, table):
        gridlib.Grid.__init__(self, parent, -1)

        self.SetTable(table)
        self.AutoSizeColumns(True)


# ---------------------------------------------------------------------------
class MainFrame(wx.Frame):
    def __init__(self, parent, datasource: DataSource):
        wx.Frame.__init__(self, parent, -1, "Table Content EXporter", size=(640, 480))
        panel = wx.Panel(self, -1, style=0)
        self.async_model = AsyncModel(datasource)
        self.table = GridTable(self.async_model)
        grid = GridView(panel, self.table)

        # grid.SetReadOnly(5, 5, True)

        export_to_csv_button = wx.Button(panel, -1, "Export to CSV")
        export_to_csv_button.SetDefault()
        box_sizer = wx.BoxSizer(wx.VERTICAL)
        box_sizer.Add(grid, 1, wx.GROW | wx.ALL, 5)
        box_sizer.Add(export_to_csv_button)
        panel.SetSizer(box_sizer)

        status_bar = wx.StatusBar(self)
        self.SetStatusBar(status_bar)

        self.controller = Controller(self.table, self.set_status_bar_text)
        self.Bind(wx.EVT_BUTTON, self.export_to_csv, export_to_csv_button)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def set_status_bar_text(self, text):
        self.GetStatusBar().SetStatusText(text)

    def export_to_csv(self, event):
        asyncio.run(self.controller.load_and_export_table_content())

    def init_load(self):
        asyncio.run(self.controller.load_and_fill_table_names())

    def on_close(self, event):
        self.Destroy()
