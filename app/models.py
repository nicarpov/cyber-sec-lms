# models will be here later
user = {
    "id": 1,
    "name": "Dmitry",
    "password": "123",
}

labs = {
    "1":{
        "name": "ЛР2.1 Администрирование межсетевых экранов",
        "manual_path": "manuals/ЛР2_1.pdf"    
    },
    "2": {
        "name": "ЛР2.2 Администрирование сетевых систем обнаружения вторжений",
        "manual_path": "manuals/ЛР2_2.pdf" 
    },
    "3": {
        "name": "ЛР2.3 Администрирование сетевых систем предотвращения вторжений",
        "manual_path": "manuals/ЛР2_3.pdf" 
    },
    "4":{
        "name": "ЛР3.1 Средства MTD для защиты компьютерных сетей",
        "manual_path": "manuals/ЛР3_1.pdf" 
    }
}

current_lab = {}
task_id = []

hosts = ['10.0.0.10', '10.0.0.20', '10.0.0.30']

