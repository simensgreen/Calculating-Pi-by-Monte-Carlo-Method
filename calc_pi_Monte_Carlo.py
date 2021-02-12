from tkinter import Tk, Canvas
import tkinter as tk
from random import randint
from math import pi


def calc_avg():
    accumulator = 0
    counter = 0

    def avg(*values):
        nonlocal accumulator
        nonlocal counter
        if values:
            accumulator += sum(values)
            counter += len(values)
        else:
            if counter != 0:
                return accumulator / counter
            else:
                return accumulator

    return avg


class CanvasTemplate:
    font = 'Comic Sans MS', 15

    def __init__(self, width, height, bg='#2B2B2B', fg='#AFB9BA'):
        width = int(width)
        height = int(height)
        self.canvas = Canvas(width=width, height=height, bg=bg)
        self.width = width
        self.height = height
        self.bg = bg
        self.fg = fg
        self.canvas_ids = {}
        self.draw()

    def delete_group(self, group_name):
        for canvas_id in self.canvas_ids.get(group_name, []):
            self.canvas.delete(canvas_id)
        self.canvas_ids[group_name] = []
        self.canvas.delete(group_name)

    def clear(self):
        for group_name in self.canvas_ids:
            self.delete_group(group_name)
        self.canvas.delete('for clear')

    def convert_canvas_to_decart(self, coords):
        return coords[0] + self.center[0], self.center[1] - coords[1]

    def draw(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    @property
    def center(self):
        return self.width / 2, self.height / 2


class Chart(CanvasTemplate):
    pi_line_color = '#499C54'
    upper_text_color = '#648658'

    chart_line_opts = {
        'fill': '#4096C1',
        'width': 4
    }

    avg_color = '#ECBB06'

    error = 0
    amount = 0
    amount_in = 0
    calc_pi = 0

    chart_line = None

    def __init__(self, width, height):
        super().__init__(width, height)
        self.chart_step = width / 100
        self.avg = calc_avg()

    def __draw_pi_line(self):
        """
        Отрисовка линии, которая соответствует точному значению числа pi.
        """
        self.delete_group('pi line')
        self.canvas_ids['pi line'] = [self.canvas.create_line(0, self.center[1],
                                                              self.width, self.center[1],
                                                              fill=self.pi_line_color,
                                                              tags=('pi line',))]

    def __draw_avg_line(self):
        self.delete_group('avg')
        height = self.height - (self.height * pi) / (self.calc_pi * 2)
        self.canvas_ids['avg'].append(self.canvas.create_line(
            0, height, self.width, height, fill=self.avg_color
        ))
        self.canvas_ids['avg'].append(self.canvas.create_text(
            self.width * .7, height + self.height * .1, text=str(self.avg()), fill=self.avg_color, font=self.font
        ))

    def __draw_upper_text(self):
        self.delete_group('upper text')

        self.canvas_ids['upper text'].append(self.canvas.create_text(
            self.center[0], self.height / 10 - self.font[1] / 2, text=f'Истинное 𝝅 = {pi}',
            fill=self.upper_text_color, tags=('upper text',), font=self.font
        ))
        self.canvas_ids['upper text'].append(self.canvas.create_text(
            self.center[0], self.height / 10 + self.font[1], text='Погрешность = %.12f' % self.error + '%',
            fill=self.upper_text_color, tags=('upper text',), font=self.font
        ))

    def __draw_footer_text(self):
        self.delete_group('footer text')

        self.canvas_ids['footer text'].append(self.canvas.create_text(
            self.center[0], self.height * .9 - self.font[1], text=f'Общее количество точек: {self.amount}',
            fill=self.fg, tags=('footer text',), font=self.font
        ))
        self.canvas_ids['footer text'].append(self.canvas.create_text(
            self.center[0], self.height * .9 + self.font[1] / 2, text=f'Точки в круге: {self.amount_in}',
            fill=self.fg, tags=('footer text',), font=self.font
        ))

    def __draw_chart(self):
        self.canvas.delete(self.chart_line)
        self.chart_line = self.canvas.create_line(0, self.center[1], 0, self.center[1],
                                                  **self.chart_line_opts)

    def __update_chart_line(self):
        self.canvas.coords(self.chart_line, *self.__get_chart_line_coords(self.canvas.coords(self.chart_line)))

    def __get_chart_line_coords(self, coords):

        def scale(coords_):
            for no, coord in enumerate(coords_):
                yield coord / 2 if no % 2 == 0 else coord

        if coords[-2] + self.chart_step > self.width * 9 / 10:
            coords = list(scale(coords))
            self.chart_step /= 2
        coords.append(coords[-2] + self.chart_step)
        coords.append(self.height - (self.height * pi) / (self.calc_pi * 2))
        return coords

    def draw(self):
        self.__draw_pi_line()
        self.__draw_upper_text()
        self.__draw_footer_text()
        self.__draw_chart()

    def update(self):
        self.__draw_footer_text()
        self.__draw_upper_text()
        self.__update_chart_line()
        self.avg(self.calc_pi)
        self.__draw_avg_line()


class Tab(CanvasTemplate):
    columns = 'Кол-во точек', 'Число pi', 'Погрешность'

    data = []
    num_of_rows = 1

    def __draw_grid(self):
        self.delete_group('grid')

        for width in range(0, self.width, self.column_width):
            line = self.canvas.create_line((width, 0), (width, self.height),
                                           fill=self.fg, tags=('grid',))
            self.canvas_ids['grid'].append(line)

        for height in range(0, self.height, self.row_height):
            line = self.canvas.create_line((self.width, height), (0, height),
                                           fill=self.fg, tags=('grid',))
            self.canvas_ids['grid'].append(line)

    def __draw_header(self):
        self.delete_group('header')

        self.canvas_ids['header'] = [
            self.canvas.create_text(self.column_width * no + self.column_width / 2, self.row_height / 2,
                                    text=cell, font=self.font, fill=self.fg)
            for no, cell in enumerate(self.columns)]

    def insert_data(self, data):
        self.delete_group('data')
        data = list(data)
        if len(data) != len(self.columns):
            raise IndexError('data len must be equal to number of columns')
        self.data.append(data)
        for row, data_row in enumerate(self.data[-(self.num_of_rows - 1):]):
            row += 1
            for column, data in enumerate(data_row):
                self.canvas_ids['data'].append(
                    self.canvas.create_text(self.column_width * column + self.column_width / 2,
                                            self.row_height * row + self.row_height / 2,
                                            text=data, fill=self.fg, tags=('data',), font=self.font)
                )

    def draw(self):
        self.__draw_grid()
        self.__draw_header()

    def update(self):
        pass

    @property
    def row_height(self):
        min_spacing = self.font[1] * 2
        divider = 10
        spacing = self.height / divider
        while spacing < min_spacing:
            divider -= 1
            if divider == 0:
                raise RuntimeError('not enough height to create table')
            spacing = self.height / divider
        self.num_of_rows = divider
        return round(spacing)

    @property
    def column_width(self):
        return int(self.width / len(self.columns))


class Quarter(CanvasTemplate):
    quarter_options = {
        'start': 0,
        'extent': -90,
        'width': 2,
        'outline': 'gray',
        'fill': '#3C3F41',
        'tags': ('quarter',)
    }

    points_options = {
        'radius': 3,
        'width': 0,
    }

    points_fill = '#ECBB06'
    points_in_quarter_fill = '#4096C1'

    points_limit = 750
    points_per_step = 10

    amount_of_points = 0
    amount_of_points_in = 0

    def __draw_quarter(self):
        self.delete_group('quarter')

        self.canvas_ids['quarter'] = [self.canvas.create_arc(-self.width, -self.height,
                                                             self.width, self.height,
                                                             **self.quarter_options)]

    def __draw_point(self, xy, radius, **options):
        x, y = xy
        self.canvas_ids['points'].append(self.canvas.create_rectangle(x - radius, y - radius, x + radius, y + radius,
                                                                      tags=('points',), **options))
        if len(self.canvas_ids['points']) > self.points_limit:
            self.canvas.delete(self.canvas_ids['points'].pop(0))

    def __point_in_quarter(self, xy):
        x, y = xy
        return True if x ** 2 + y ** 2 <= self.width ** 2 else False

    def draw_points(self):
        for point_no in range(self.points_per_step):
            xy = randint(0, self.width), randint(0, self.height)
            if self.__point_in_quarter(xy):
                fill = self.points_in_quarter_fill
                self.amount_of_points_in += 1
            else:
                fill = self.points_fill
            self.__draw_point(xy, fill=fill, **self.points_options)
            self.amount_of_points += 1

    def draw(self):
        if self.canvas_ids.get('points') is None:
            self.canvas_ids['points'] = []
        self.__draw_quarter()
        self.draw_points()

    def update(self):
        self.draw_points()


class App:
    data_size_power = 1
    data_size_factor = 0

    def __init__(self):
        self.root = Tk()
        self.quarter = Quarter(720, 720)
        self.tab = Tab(self.quarter.width * .58, self.quarter.height / 1.44)
        self.chart = Chart(self.tab.width, self.quarter.height - self.tab.height)

        self.quarter.canvas.pack(side=tk.LEFT)
        self.tab.canvas.pack()
        self.chart.canvas.pack(side=tk.BOTTOM)

    def _process(self):
        self.running = self.root.after(16, self._process)
        self._math_process()
        self._draw_process()

    def _math_process(self):
        self.quarter.draw_points()
        self.chart.calc_pi = self.quarter.amount_of_points_in / self.quarter.amount_of_points * 4
        self.chart.amount = self.quarter.amount_of_points
        self.chart.amount_in = self.quarter.amount_of_points_in
        self.chart.error = abs(self.chart.calc_pi - pi) / pi * 100

        if self.chart.amount >= 10 ** self.data_size_power * self.data_size_factor:
            self.data_size_factor += 1
            self.tab.insert_data([str(self.chart.amount), "%.8f" % self.chart.calc_pi, "%7f" % self.chart.error + '%'])
            if self.data_size_factor >= 10:
                self.data_size_power += 1
                self.data_size_factor = 0

    def _draw_process(self):
        self.quarter.update()
        self.chart.update()
        self.tab.update()

    def run(self):
        self._process()
        self.root.mainloop()


if __name__ == '__main__':
    app = App()
    app.run()
