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

    # Ward councillors (in the order supplied by the council)
    'councillor_amaokpala': {
        'name': '',
        'office': 'Councillor, Amaokpala Ward',
        'photo': 'councillors/amaokpala.jpg',
    },
    'councillor_nanka_2': {
        'name': 'Hon. Obinna Lotanna Nnamdi',
        'office': 'Councillor, Nanka Ward 2',
        'photo': 'councillors/nanka-2.jpg',
    },
    'councillor_omogho': {
        'name': 'Oguguo Josephat E.',
        'office': 'Councillor, Omogho Ward',
        'photo': 'councillors/omogho.jpg',
    },
    'councillor_ufuma_2': {
        'name': 'Nwankwo Chinedu Vincent',
        'office': 'Councillor, Ufuma Ward 2',
        'photo': 'councillors/ufuma-2.jpg',
    },
    'councillor_ufuma_1': {
        'name': 'Hon. Nwafor Chidi Joel',
        'office': 'Councillor, Ufuma Ward 1',
        'photo': 'councillors/ufuma-1.jpg',
    },
    'councillor_ajalli_2': {
        'name': 'Mazi Godwin Okey Nworie, JP',
        'office': 'Councillor, Ajalli Ward 2',
        'photo': 'councillors/ajalli-2.jpg',
    },
    'councillor_amaetiti': {
        'name': 'Okoye Chidera David',
        'office': 'Councillor, Amaetiti Ward',
        'photo': 'councillors/amaetiti.jpg',
    },
    'councillor_awgbu_1': {
        'name': 'Ogboo Helen Chinwoke',
        'office': 'Councillor, Awgbu Ward 1',
        'photo': 'councillors/awgbu-1.jpg',
    },
    'councillor_ndiokolo_ndiokpaleke': {
        'name': 'Japhet Ndubuisi Okoli',
        'office': 'Councillor, Ndiokolo-Ndiokpaleke Ward',
        'photo': 'councillors/ndiokolo-ndiokpaleke.jpg',
    },
    'councillor_awgbu_2': {
        'name': 'Okoye Obiora Samuel',
        'office': 'Councillor, Awgbu Ward 2',
        'photo': 'councillors/awgbu-2.jpg',
    },
    'councillor_ndiowu': {
        'name': 'William Alex Omenukor',
        'office': 'Councillor, Ndiowu Ward',
        'photo': 'councillors/ndiowu.jpg',
    },
}

# Order in which ward councillors are listed
COUNCILLORS = [
    'councillor_amaokpala',
    'councillor_nanka_2',
    'councillor_omogho',
    'councillor_ufuma_2',
    'councillor_ufuma_1',
    'councillor_ajalli_2',
    'councillor_amaetiti',
    'councillor_awgbu_1',
    'councillor_ndiokolo_ndiokpaleke',
    'councillor_awgbu_2',
    'councillor_ndiowu',
]
