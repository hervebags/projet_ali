import requests
from bs4 import BeautifulSoup
import json
import re



"""""    with open('data.json', 'a', encoding='utf8') as file:

        json.dump(resultat, file, ensure_ascii=False, indent=2)
"""
def find_data_GCA():
    data_json = None

    def findWholeWord(w):
        return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

    def type_recette(soup, titre):
        reccete = soup.find(class_='mwsgeneric-base-html parbase section')
        reccete1 = reccete.find_all(class_='wb-eqht')
        d = 0
        reccte_type = 'None'

        for reccete2 in reccete1:
            reccete3 = reccete2.get_text()
            d = d + 1
            for i in reccete3.splitlines():
                if titre == i:
                    if d == 1:
                        reccte_type = 'Déjeuner'

                        return reccte_type
                    elif d == 2:
                        reccte_type = 'Souper'
                        return reccte_type
                    elif d == 3:
                        reccte_type = 'Collations'
                        return reccte_type
        return reccte_type

    # reccete list
    page = requests.get(
        'https://www.canada.ca/fr/sante-canada/services/guide-alimentaire-canadien/conseils-alimentation-saine/planification-repas-cuisine-choix-sante/recettes.html')
    soup_1 = BeautifulSoup(page.text, 'html.parser')

    reccete = soup_1.find_all(class_='sect-lnks media')
    print('il ya ' + str(reccete.__len__())+"recettes")
    print()

    data = []
    k = 1
    for link0 in reccete:
        print(k)
        k = k + 1
        titre = link0.find(class_="media-heading").get_text()
        link5 = link0.find(class_="media-body").get_text()
        link2 = link0.find('a')
        lien0 = link2.get('href')
        description = link0.find('p').getText()
        image0 = link0.find('img')
        image = 'https://www.canada.ca/' + image0['src']
        lien = 'https://www.canada.ca/' + lien0
        L = lien
        page = requests.get(L)
        soup = BeautifulSoup(page.text, 'html.parser')
        mydivs = soup.find_all(class_="container")
        linkr0 = mydivs[3]
        recette = linkr0.find(class_="tabpanels")

        # ingrédients -------------------------
        ingrédients = recette.find_all('ul')
        #

        ingrédients_final = []

        for ingr in ingrédients:
            valeur = []
            for i in ingr.get_text().splitlines():
                for s in i.split():
                    if s.replace(',', '').isdigit() or s.replace('/', '').isdigit():
                        valeur.append(s)

                if not (not i):
                    if valeur.__len__() > 0:
                        ingrédients_final.append({'ingrédient': i, 'valeur': valeur[0]})
                    else:
                        ingrédients_final.append({'ingrédient': i, 'valeur': 'null'})

                    valeur.clear()

        # preparation-------------------

        préparation_final = []
        pre_t = linkr0.find(class_="panel-body")
        pre_t = pre_t.find_all('li')
        for p in pre_t:
            pre = p.get_text()
            for i in pre.splitlines():
                if i.__len__() > 0:
                    préparation_final.append(i)

        # ----------------------------------------------------
        truc = linkr0.find(class_="panel-body")
        truc0 = truc.find_all('li')
        truc_final = []
        for ingr in truc0:
            truc_final.append(ingr.get_text())

        p = soup.find_all('p')
        # partie categorie / cuisson / temps / portion

        for i in p:
            if findWholeWord('Catégories')(i.get_text()):
                categorie0 = i.get_text().split(':')


                categorie = categorie0[1].replace('\xa0', ' ').split(',')
                print(categorie)

            if findWholeWord('préparation')(i.get_text()) and findWholeWord('cuisson')(i.get_text()):
                result = i.get_text()
                for i in result.splitlines():
                    if findWholeWord('préparation')(i):
                        préparation = i.split(':')
                        temps0 = préparation[1].split(' ')
                        temps1 = temps0[1].split(' ')
                        temps = temps1[0]

                    if findWholeWord('cuisson')(i):
                        cuisson0 = i.split(':')
                        cuisson1 = cuisson0[1].split(' ')
                        cuisson = cuisson1[1]

                    if findWholeWord('Portions')(i):
                        protions0 = i.split(':')
                        protions1 = protions0[1].split(' ')
                        protions = protions1[1]

        type_ = type_recette(soup_1, titre)
        resultat = {"titre": titre, "type": type_, "description": description, "image": image, "link": lien,
                    "ingrédients": ingrédients_final, "préparation": préparation_final, "truc": truc_final,
                    'cuisson': cuisson, 'portion': protions, 'temps': temps,
                    'Catégories': categorie}

        data.append(resultat)

    with open('data.txt', 'w', encoding='utf8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=2)

