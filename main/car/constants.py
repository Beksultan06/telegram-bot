from django.utils.translation import ugettext_lazy as _


# Виды двигателя
GASOLINE = 'gasoline'
GAS = 'gas'
GASOLINE_GAZ = 'gasoline/gas'
DIESEL = 'diesel'
HYBRID = 'hybrid'
ELECTRIC = 'electric'

engines = (
    (GASOLINE, _('Бензин')),
    (GAS, _('Газ')),
    (GASOLINE_GAZ, _('Бензин/газ')),
    (DIESEL, _('Дизель')),
    (HYBRID, _('Гибрид')),
    (ELECTRIC, _('Электро')),
)

# Виды КПП
MANUAL = 'manual'
AUTOMATIC = 'automatic'
VARIATOR = 'variator'
ROBOT = 'robot'

transmissions = (
    (MANUAL, _('Механика')),
    (AUTOMATIC, _('Автомат')),
    (VARIATOR, _('Вариатор')),
    (ROBOT, _('Робот')),
)