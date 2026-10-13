"""
Single register of named officials.

Every page shows a person through this register (see templates/_people.html),
so each individual has exactly one name, one office and one photo site-wide.
To change someone's office or photo, edit it here only.
"""

PEOPLE = {
    'chairman': {
        'name': 'Hon. Barr. Casmir Chinonso Nwafor',
        'office': 'Executive Chairman',
        'photo': 'chairman-portrait.jpg',
    },
    'vice_chairman': {
        'name': 'Hon. Ifesinachi Chukwurah',
        'office': 'Vice Chairman',
        'photo': 'orumbamember21.jpg',
    },
    'health_supervisor': {
        'name': 'Hon. Mrs Christiana Nwankwo',
        'office': 'Supervisor for Health',
        'photo': 'orumbamember12.jpg',
    },
    'works_supervisor': {
        'name': 'Engr. Austin Ganco O.',
        'office': 'Supervisor for Works & Housing',
        'photo': 'orumbamember11.jpg',
    },
    'finance_supervisor': {
        'name': 'Hon. Kingsley Eche Ngugu',
        'office': 'Supervisor for Budget & Finance',
        'photo': 'orumbamember15.jpg',
    },
    'youth_supervisor': {
        'name': 'Hon. Chibuike Jasper Ezeifedikwa',
        'office': 'Supervisor for Youth, Sports & Culture',
        'photo': 'orumbamember19.jpg',
    },
    'health_committee_chairman': {
        'name': 'Hon. Williams Omenuko',
        'office': 'Chairman, House Committee on Health',
        'photo': 'orumbamember1.jpg',
    },
    'deputy_leader': {
        'name': 'Hon. Nwankwo Ikenna Kenneth',
        'office': 'Deputy Leader, Congress of Councilors',
        'photo': 'orumbamember6.jpg',
    },
    'information_adviser': {
        'name': 'Arinze Clems',
        'office': 'Special Adviser on Information',
        'photo': 'orumbamember8.jpg',
    },
    'chairman_pa': {
        'name': 'Nwosu Izuchukwu Innocent',
        'office': 'Personal Assistant to the Executive Chairman',
        'photo': 'orumbamember10.jpg',
    },
    'vice_chairman_sa': {
        'name': 'Onwurah Chukwuebuka Frank',
        'office': 'Special Assistant to the Vice Chairman',
        'photo': 'orumbamember14.jpg',
    },
}
