from django import template
from django.utils.safestring import mark_safe
from storeapp.models import Smartphones

register = template.Library()

TABLE_HEAD = '''
                <table class="table">
                  <tbody>
             '''

TABLE_TAIL = '''
                  </tbody>
                </table>
             '''

TABLE_CONTENT = '''
                <tr>
                  <td>{name}</td>
                  <td>{value}</td>
                </tr>
                '''

PRODUCT_SPEC = {
    'smartphones': {
        'Диагональ': 'diagonal',
        'Тип дисплея': 'display_type',
        'Разрешение экрана*': 'input_resolution',
        'Разрешение экрана': 'resolution',
        'Объем аккумулятора': 'accum_value',
        'Оперативная память': 'ram',
        'Поддержка sd накопителя': 'sd',
        'Максимальный объем sd карты': 'sd_values_max',
        'Фронтальная камера (в мегапикселях)': 'frontal_cam_mp',
        'Основная камера (в мегапикселях)': 'main_cam_mp',
    },

    'noteboocks': {
        'Диагональ': 'diagonal',
        'Тип дисплея': 'display_type',
        'астота процессора': 'processor_freq',
        'Оперативная память': 'ram',
        'Видеокарта': 'video',
        'Время работы аккумулятора': 'time_without_charge',
    }
}

def get_product_spec(product, model_name):
    table_content = ''
    for name, value in PRODUCT_SPEC[model_name].items():
        table_content += TABLE_CONTENT.format(name=name, value=getattr(product, value))
    return table_content


@register.filter
def product_spec(product):
    model_name = product.__class__._meta.model_name
    if isinstance(product, Smartphones):
        if not product.sd:
            try:
                PRODUCT_SPEC['smartphones'].pop('Максимальный объем sd карты')
            except KeyError:
                pass
        else:
            PRODUCT_SPEC['smartphones']['Максимальный объем sd карты'] = 'sd_values_max'

        if not product.unstandart_resolution:
            try:
                PRODUCT_SPEC['smartphones'].pop('Разрешение экрана*')
            except KeyError:
                pass
        else:
            PRODUCT_SPEC['smartphones'].pop('Разрешение экрана')
    return mark_safe(TABLE_HEAD + get_product_spec(product, model_name) + TABLE_TAIL)