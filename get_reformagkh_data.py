#!/usr/bin/env python -u
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# get_reformagkh_data.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# About: Grab reformagkh.ru data on buildings, put it in the CSV table.
# Created: 18.03.2014
# Usage example: python get_reformagkh_data.py
# ---------------------------------------------------------------------------

from bs4 import BeautifulSoup
import urllib2
import csv
from progressbar import *
from httplib import BadStatusLine,IncompleteRead
import socket


def console_out(text):
    #write httplib error messages to console
    time_current = datetime.datetime.now()
    timestamp = time_current.strftime('%Y-%m-%d %H:%M:%S')
    
    f_errors.write(timestamp + ": "+ text)

def urlopen_house(link,id):
    #fetch html data on a house
    numtries = 5
    timeoutvalue = 40
    
    for i in range(1,numtries+1):
        i = str(i)
        try:
            u = urllib2.urlopen(link, timeout = timeoutvalue)
        except BadStatusLine:
            console_out('BadStatusLine for ID:' + id + '.' + ' Attempt: ' + i)
            res = False
            time.sleep(3)
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                console_out('We failed to reach a server for ID:' + id + ' Reason: ' + str(e.reason) + '.' + ' Attempt: ' + i)
            elif hasattr(e, 'code'):
                console_out('The server couldn\'t fulfill the request for ID: ' + id + ' Error code: ' + str(e.code) + '.' + ' Attempt: ' + i)
            res = False
            time.sleep(3)
        except socket.timeout, e:
            console_out('Connection timed out on urlopen() for ID: ' + id + '.' + ' Attempt: ' + i)
            res = False
            time.sleep(3)
        else:
            try:
                r = u.read()
            except socket.timeout, e:
                console_out('Connection timed out on socket.read() for ID: ' + id + '.' + ' Attempt: ' + i)
                res = False
                u.close()
                time.sleep(3)
            except IncompleteRead:
                console_out('Incomplete read on socket.read() for ID: ' + id + '.' + ' Attempt: ' + i)
                res = False
                u.close()
                time.sleep(3)
            else:
                res = r
                break
    
    return res

def extract_value(mkdtable,code):
  #extract value for general attributes
  tr = mkdtable.find('td', {'class':'col-num'}, text = str(code)).parent
  if tr.find('td',{'class':'b-td_value-def'}):
      res = tr.find('td',{'class':'b-td_value-def'}).text.strip()
  elif len(tr.findAll("td")) == 3:
      res = tr.findAll("td")[2].text.strip()
      
  return res

def extract_value_descr(mkdtable):
  #extract value for description field
  div = mkdtable.find("div",{'style':'position: relative;'})
  if div.find("p"):
        res = div.find("p").text.strip()
  else:
        res = div.text.strip()
  return res

def extract_value_constr(mkdtable):
  #extract value for construction features field

  #TODO deal with popup text boxes that might(?) contain more information, currently only first non-null <p> is being returned
  div = mkdtable.findAll('div',{'style':'position: relative;'})[1]
  if len(div.findAll('p')) > 0:
      if div.findAll('p')[0] != '': 
        res = div.findAll('p')[0].text
      else:
        res = div.findAll('p')[1].text
  else:
      res = div.text.strip()

  return res

def extract_value_area(mkdtable):
  #extract values for various living area
  areas = mkdtable.findAll('tr',{'class':'field_tp_square_all'})

  return areas[0].findAll('td')[2].text,areas[1].findAll('td')[2].text,areas[2].findAll('td')[2].text

def extract_value_heat(mkdtable):
  #extract values for heat exchange
  heats = mkdtable.findAll('tr',{'class':'group_tp_building_term_charact'})

  return heats[0].findAll('td')[2].text,heats[1].findAll('td')[2].text

def get_housedata(link,house_id,lvl1_name,lvl1_id,lvl2_name,lvl2_id):
  #process house data to get main attributes
    res = urlopen_house(link + "/view/" + house_id,house_id)
    
    if res != False:
        soup = BeautifulSoup(''.join(res))
        
        address = soup.find("div", { "class" : "border-block" }).find("h1").find("span").text
        mkdtables = soup.findAll("table", { "class" : "mkd-table" })
        
        #GENERAL
        mkdtable = mkdtables[0]
        trs = mkdtable.findAll("tr")

        area = trs[0].findAll("td")[1].text                              #gen1
        area_live = trs[3].findAll("td")[1].text                         #gen2
        area_nonlive = trs[3].findAll("td")[1].text                      #gen3
        area_general = trs[3].findAll("td")[1].text                      #gen4

        mkdtable = mkdtables[1]
        trs = mkdtable.findAll("tr")

        cad_no = trs[0].findAll("td")[1].text                            #gen5
        year = trs[1].findAll("td")[1].text                              #gen6
        status = trs[2].findAll("td")[1].text                            #gen7
        mgmt_company = trs[3].findAll("td")[1].text                      #gen8
        if trs[3].findAll("td")[1].find("a"):
            mgmt_company_link = "http://www.reformagkh.ru" + trs[3].findAll("td")[1].find("a")['href']                                                             #gen9
        else:
            mgmt_company_link = ""
        
        
        #PASSPORT
        ##GENERAL
        mkdtable = mkdtables[2]

        serie = extract_value(mkdtable, '1')                            #1
        descript = extract_value_descr(mkdtable)                        #2
        house_name = extract_value(mkdtable, '3')                       #3
        house_type = extract_value(mkdtable, '4')                       #4
        year2 = extract_value(mkdtable, '5')                            #5
        wall_mat = extract_value(mkdtable, '6')                         #6
        perekr_type = extract_value(mkdtable, '7')                      #7
        levels = extract_value(mkdtable, '8')                           #8
        doors = extract_value(mkdtable, '9')                            #9
        elevators = extract_value(mkdtable, '10')                       #10
        area2 = extract_value(mkdtable, '11')                           #11
        area_live_total = extract_value(mkdtable, '12')                 #12
        area_live_priv,area_live_munic,area_live_state =  extract_value_area(mkdtable)
        area_nonlive2 = extract_value(mkdtable, '13')                   #13
        area_uch = extract_value(mkdtable, '14')                        #14
        area_near = extract_value(mkdtable, '15')                       #15
        no_inventory = extract_value(mkdtable, '16')                    #16
        cad_no2 = extract_value(mkdtable, '17')                         #17
        apts = extract_value(mkdtable, '18')                            #18
        people = extract_value(mkdtable, '19')                          #19
        accounts = extract_value(mkdtable, '20')                        #20
        constr_feat = extract_value_constr(mkdtable)                    #21
        heat_fact,heat_norm = extract_value_heat(mkdtable)
        energy_class = extract_value(mkdtable, '23')                    #22
        energy_audit_date = extract_value(mkdtable, '24')               #23
        privat_date = extract_value(mkdtable, '25')                     #24
        
        statstable = soup.find("table", { "class" : "statistic" })
        trs = statstable.findAll("tr")

        wear_tot = trs[0].findAll("td")[1].text.strip()                  #stat1
        wear_fundament = trs[1].findAll("td")[1].text.strip()            #stat2
        wear_walls = trs[2].findAll("td")[1].text.strip()                #stat3
        wear_perekr = trs[3].findAll("td")[1].text.strip()               #stat4
        state = soup.find("div", { "class" : "block-title" }).find('span').text  #stat5
        
        ##CONSTRUCTION
        mkdtable = mkdtables[3]

        ###Facade
        facade_area_tot = extract_value(mkdtable, '1')                   #1
        facade_area_sht = extract_value(mkdtable, '2')                   #2
        facade_area_unsht = extract_value(mkdtable, '3')                 #3
        facade_area_panel = extract_value(mkdtable, '4')                 #4
        facade_area_plit = extract_value(mkdtable, '5')                  #5
        facade_area_side = extract_value(mkdtable, '6')                  #6
        facade_area_wood = extract_value(mkdtable, '7')                  #7
        facadewarm_area_sht = extract_value(mkdtable, '8')               #8
        facadewarm_area_plit = extract_value(mkdtable, '9')              #9
        facadewarm_area_side = extract_value(mkdtable, '10')              #10
        facade_area_otmost = extract_value(mkdtable, '11')                #11
        facade_garea_glassw = extract_value(mkdtable, '12')               #12
        facade_garea_glassp = extract_value(mkdtable, '13')               #13
        facade_iarea_glassw = extract_value(mkdtable, '14')               #14
        facade_iarea_glassp = extract_value(mkdtable, '15')               #15
        facade_area_door_met = extract_value(mkdtable, '16')              #16
        facade_area_door_oth = extract_value(mkdtable, '17')              #17
        facade_capfix_year = extract_value(mkdtable, '18')                #18
        ###Roof
        roof_area_tot = extract_value(mkdtable, '19')                     #19
        roof_area_shif = extract_value(mkdtable, '20')                    #20
        roof_area_met = extract_value(mkdtable, '21')                     #21
        roof_area_oth = extract_value(mkdtable, '22')                     #22
        roof_area_flat = extract_value(mkdtable, '23')                    #23
        roof_capfix_year = extract_value(mkdtable, '24')                  #24
        ###Basement
        base_descr = extract_value(mkdtable, '25')                        #25
        base_area = extract_value(mkdtable, '26')                         #26
        base_capfix_year = extract_value(mkdtable, '27')                  #27
        ###Public areas
        publ_area = extract_value(mkdtable, '28')                         #28
        publ_capfix_year = extract_value(mkdtable, '29')                  #29
        ###Tras
        trash_num = extract_value(mkdtable, '30')                         #30
        trash_capfix_year = extract_value(mkdtable, '31')                 #31

        ##NETWORKS
        mkdtable = mkdtables[4]
        
        ###heating
        
        ###hot water
        
        ###cold water
        
        ###sewage
        
        ###electricity
        
        ###gas
        
        
        ##ELEVATORS
        
        #MANAGEMENT
        #res = urllib2.urlopen(link + "/management/" + house_id)
        #soup = BeautifulSoup(''.join(res))
        
        #FINANCE
        #res = urllib2.urlopen(link + "/finance/" + house_id)
        #soup = BeautifulSoup(''.join(res))
        
        #write to output
        csvwriter_housedata.writerow(dict(HOUSE_ID=house_id,
                                          ADDRESS=address.encode("utf-8"),
                                          AREA=area.encode("utf-8"),
                                          AREA_LIVE=area_live.encode("utf-8"),
                                          AREA_NONLIVE=area_nonlive.encode("utf-8"),
                                          AREA_GENERAL=area_general.encode("utf-8"),
                                          CAD_NO=cad_no.encode("utf-8"),
                                          YEAR=year.encode("utf-8"),
                                          STATUS=status.encode("utf-8"),
                                          MGMT_COMPANY=mgmt_company.encode("utf-8"),
                                          MGMT_COMPANY_LINK=mgmt_company_link.encode("utf-8"),
                                          SERIE=serie.encode("utf-8"),
                                          DESCRIPT=descript.encode("utf-8"),
                                          HOUSE_NAME=house_name.encode("utf-8"),
                                          HOUSE_TYPE=house_type.encode("utf-8"),
                                          YEAR2=year2.encode("utf-8"),
                                          WALL_MAT=wall_mat.encode("utf-8"),
                                          PEREKR_TYPE=perekr_type.encode("utf-8"),
                                          LEVELS=levels.encode("utf-8"),
                                          DOORS=doors.encode("utf-8"),
                                          ELEVATORS=elevators.encode("utf-8"),
                                          AREA2=area2.encode("utf-8"),
                                          AREA_LIVE_TOTAL=area_live_total.encode("utf-8"),
                                          AREA_LIVE_PRIV=area_live_priv.encode("utf-8"),
                                          AREA_LIVE_MUNIC=area_live_munic.encode("utf-8"),
                                          AREA_LIVE_STATE=area_live_state.encode("utf-8"),
                                          AREA_NONLIVE2=area_nonlive2.encode("utf-8"),
                                          AREA_UCH=area_uch.encode("utf-8"),
                                          AREA_NEAR=area_near.encode("utf-8"),
                                          NO_INVENTORY=no_inventory.encode("utf-8"),
                                          CAD_NO2=cad_no2.encode("utf-8"),
                                          APTS=apts.encode("utf-8"),
                                          PEOPLE=people.encode("utf-8"),
                                          ACCOUNTS=accounts.encode("utf-8"),
                                          CONSTR_FEAT=constr_feat.encode("utf-8"),
                                          HEAT_FACT=heat_fact.encode("utf-8"),
                                          HEAT_NORM=heat_norm.encode("utf-8"),
                                          ENERGY_CLASS=energy_class.encode("utf-8"),
                                          ENERGY_AUDIT_DATE=energy_audit_date.encode("utf-8"),
                                          PRIVAT_DATE=privat_date.encode("utf-8"),
                                          WEAR_TOT=wear_tot.encode("utf-8"),
                                          WEAR_FUNDAMENT=wear_fundament.encode("utf-8"),
                                          WEAR_WALLS=wear_walls.encode("utf-8"),
                                          WEAR_PEREKR=wear_perekr.encode("utf-8"),
                                          STATE=state.encode("utf-8"),
                                          FACADE_AREA_TOT=facade_area_tot.encode("utf-8"),
                                          FACADE_AREA_SHT=facade_area_sht.encode("utf-8"),
                                          FACADE_AREA_UNSHT=facade_area_unsht.encode("utf-8"),
                                          FACADE_AREA_PANEL=facade_area_panel.encode("utf-8"),
                                          FACADE_AREA_PLIT=facade_area_plit.encode("utf-8"),
                                          FACADE_AREA_SIDE=facade_area_side.encode("utf-8"),
                                          FACADE_AREA_WOOD=facade_area_wood.encode("utf-8"),
                                          FACADEWARM_AREA_SHT=facadewarm_area_sht.encode("utf-8"),
                                          FACADEWARM_AREA_PLIT=facadewarm_area_plit.encode("utf-8"),
                                          FACADEWARM_AREA_SIDE=facadewarm_area_side.encode("utf-8"),
                                          FACADE_AREA_OTMOST=facade_area_otmost.encode("utf-8"),
                                          FACADE_GAREA_GLASSW=facade_garea_glassw.encode("utf-8"),
                                          FACADE_GAREA_GLASSP=facade_garea_glassp.encode("utf-8"),
                                          FACADE_IAREA_GLASSW=facade_iarea_glassw.encode("utf-8"),
                                          FACADE_IAREA_GLASSP=facade_iarea_glassp.encode("utf-8"),
                                          FACADE_AREA_DOOR_MET=facade_area_door_met.encode("utf-8"),
                                          FACADE_AREA_DOOR_OTH=facade_area_door_oth.encode("utf-8"),
                                          FACADE_CAPFIX_YEAR=facade_capfix_year.encode("utf-8"),
                                          ROOF_AREA_TOT=roof_area_tot.encode("utf-8"),
                                          ROOF_AREA_SHIF=roof_area_shif.encode("utf-8"),
                                          ROOF_AREA_MET=roof_area_met.encode("utf-8"),
                                          ROOF_AREA_OTH=roof_area_oth.encode("utf-8"),
                                          ROOF_AREA_FLAT=roof_area_flat.encode("utf-8"),
                                          ROOF_CAPFIX_YEAR=roof_capfix_year.encode("utf-8"),
                                          BASE_DESCR=base_descr.encode("utf-8"),
                                          BASE_AREA=base_area.encode("utf-8"),
                                          BASE_CAPFIX_YEAR=base_capfix_year.encode("utf-8"),
                                          PUBL_AREA=publ_area.encode("utf-8"),
                                          PUBL_CAPFIX_YEAR=publ_capfix_year.encode("utf-8"),
                                          TRASH_NUM=trash_num.encode("utf-8"),
                                          TRASH_CAPFIX_YEAR=trash_capfix_year.encode("utf-8"),
                                          LVL1_NAME=lvl1_name.encode("utf-8"),
                                          LVL1_ID=lvl1_id,
                                          LVL1_LINK="http://www.reformagkh.ru/myhouse?tid=" + lvl1_id,
                                          LVL2_NAME=lvl2_name.encode("utf-8"),
                                          LVL2_ID=lvl2_id,
                                          LVL2_LINK="http://www.reformagkh.ru/myhouse/list?tid=" + lvl2_id,
                                          HOUSE_LINK="http://www.reformagkh.ru/myhouse/view/" + house_id))

def get_lvl1_ids(link):
    
    res = urllib2.urlopen(link)
    soup = BeautifulSoup(''.join(res.read()))
    
    locations = soup.findAll("td",{ "class" : "location" })
    lvl1_ids = {}
    for loc in locations:
        name = loc.find("a").text.strip()
        id = loc.find("a")['id'].replace("element_","")
        lvl1_ids[name] = id
    
    return lvl1_ids

def get_lvl2_ids(link):
    res = urllib2.urlopen(link)
    soup = BeautifulSoup(''.join(res.read()))
    
    locations = soup.findAll("td",{ "class" : "location" })
    lvl2_ids = {}
    for loc in locations:
        if loc.find("a"):
            name = loc.find("a").text.strip()
            id = loc.find("a")['id'].replace("element_","")
            lvl2_ids[name] = id
    
    return lvl2_ids

def get_house_list(link):
    res = urllib2.urlopen(link)
    soup = BeautifulSoup(''.join(res.read()))
    
    houses_ids = []
    houses = soup.findAll("td",{"class":"name"})
    for house in houses:
        house_id = house.find("a")['href'].split("/")[3]
        houses_ids.append(house_id)
    
    return houses_ids
    
if __name__ == '__main__':
    lvl1_link = "http://www.reformagkh.ru/myhouse?tid=2280999&sort=alphabet&item=mkd"
    house_link = "http://www.reformagkh.ru/myhouse/"
    #house_id = 8625429
    
    #init errors.log
    f_errors = open("errors.txt","wb")
    
    #init csv for housedata
    f_housedata = open("data/housedata.csv","wb")
    fieldnames_data = ("HOUSE_ID","ADDRESS","AREA","AREA_LIVE","AREA_NONLIVE","AREA_GENERAL","CAD_NO","YEAR","STATUS","MGMT_COMPANY","MGMT_COMPANY_LINK","SERIE","DESCRIPT","HOUSE_NAME","HOUSE_TYPE","YEAR2","WALL_MAT","PEREKR_TYPE","LEVELS","DOORS","ELEVATORS","AREA2","AREA_LIVE_TOTAL","AREA_LIVE_PRIV","AREA_LIVE_MUNIC","AREA_LIVE_STATE","AREA_NONLIVE2","AREA_UCH","AREA_NEAR","NO_INVENTORY","CAD_NO2","APTS","PEOPLE","ACCOUNTS","CONSTR_FEAT","HEAT_FACT","HEAT_NORM","ENERGY_CLASS","ENERGY_AUDIT_DATE","PRIVAT_DATE","WEAR_TOT","WEAR_FUNDAMENT","WEAR_WALLS","WEAR_PEREKR","STATE","FACADE_AREA_TOT","FACADE_AREA_SHT","FACADE_AREA_UNSHT","FACADE_AREA_PANEL","FACADE_AREA_PLIT","FACADE_AREA_SIDE","FACADE_AREA_WOOD","FACADEWARM_AREA_SHT","FACADEWARM_AREA_PLIT","FACADEWARM_AREA_SIDE","FACADE_AREA_OTMOST","FACADE_GAREA_GLASSW","FACADE_GAREA_GLASSP","FACADE_IAREA_GLASSW","FACADE_IAREA_GLASSP","FACADE_AREA_DOOR_MET","FACADE_AREA_DOOR_OTH","FACADE_CAPFIX_YEAR","ROOF_AREA_TOT","ROOF_AREA_SHIF","ROOF_AREA_MET","ROOF_AREA_OTH","ROOF_AREA_FLAT","ROOF_CAPFIX_YEAR","BASE_DESCR","BASE_AREA","BASE_CAPFIX_YEAR","PUBL_AREA","PUBL_CAPFIX_YEAR","TRASH_NUM","TRASH_CAPFIX_YEAR","LVL1_NAME","LVL1_ID","LVL1_LINK","LVL2_NAME","LVL2_ID","LVL2_LINK","HOUSE_LINK")
    fields_str = ",".join(fieldnames_data)
    f_housedata.write(fields_str+'\n')
    f_housedata.close()
    
    f_housedata = open("data/housedata.csv","ab")
    
    
    csvwriter_housedata = csv.DictWriter(f_housedata, fieldnames=fieldnames_data)
    
    lvl1_ids = get_lvl1_ids(lvl1_link)
    for lvl1_name in lvl1_ids:
        lvl2_ids = get_lvl2_ids("http://www.reformagkh.ru/myhouse?tid=" + lvl1_ids[lvl1_name])
        
        for lvl2_name in lvl2_ids:
            print lvl2_name
            #get list of houses
            houses_ids = get_house_list("http://www.reformagkh.ru/myhouse/list?tid=" + lvl2_ids[lvl2_name] + "&page=no")
            
            pbar = ProgressBar(widgets=[Bar('=', '[', ']'), ' ', Counter(), " of " + str(len(houses_ids)), ' ', ETA()]).start()
            pbar.maxval = len(houses_ids)
            
            i = 0
            for house_id in houses_ids:
                i = i+1
                res = get_housedata(house_link,str(house_id),lvl1_name,lvl1_ids[lvl1_name],lvl2_name,lvl2_ids[lvl2_name])
                pbar.update(pbar.currval+1)
            pbar.finish()

    f_housedata.close()
    f_errors.close()