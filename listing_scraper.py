
# coding: utf-8

# In[21]:


import requests
import pandas as pd
from bs4 import BeautifulSoup
#import re


# In[22]:


#STEP 1 - get each listing's page content and make a soup object with it for parsing.
#listing_page = requests.get('http://www.loopnet.com/Listing/1851-McCarthy-Blvd-Milpitas-CA/8445511/')
#listing_page_soup = BeautifulSoup(listing_page.content, "html.parser")


# In[23]:


#STEP 2. Finding the name/city/zipcode of the property
def name_city_zipcode(tag):
    
    title_string = tag.find('title').text
    title_list = title_string.split(',')
    #print(title_list)
    return [title_list[0], title_list[1][1:], title_list[3][1:6]]


# In[24]:


#Step 3. getting the property type of the listing
def property_type_getter(tag):
    import re
    return tag.find('td', string = re.compile('Property Type')).next_sibling.next_sibling.text[2:].split(" ")[0]


# In[25]:


#Step 4. getting the whole building's SF
def rentable_building_area_getter(tag):
    import re
    rba = tag.find('td', string = re.compile('Rentable Building Area'))
    
    if rba == None:
        gla = tag.find('td', string = re.compile('Gross Leasable Area'))
        if gla != None:
            return gla.next_sibling.next_sibling.text[2:].split(" ")[0]
        else:
            return 'Not Disclosed'
    else:
        return rba.next_sibling.next_sibling.text[2:].split(" ")[0]


# In[26]:


#Step 5. Gets the number of Spaces for that listing
def num_spaces_getter(tag):
    import re
    return int(tag.find('h3', string = re.compile("Space")).text.split(' ')[0])


# In[27]:


#Step 6. Get unique attributes for each space. ie Space Title, Rental Rate, Service Type, Space Available, Floor


# In[28]:


def service_types_getter(tag):
    import re
    service_type_list = tag.find_all('td', string=re.compile("Service Type"))
    return [service_type.next_sibling.next_sibling.text[2:] for service_type in service_type_list]
        


# In[29]:


def spaces_sqft_getter(tag):
    import re
    sqft_available_list = tag.find_all('td', string = re.compile('Space Available'))
    
    return [sq_ft.next_sibling.next_sibling.text[2:].split(sep= ' ')[0] 
            for sq_ft in sqft_available_list]


# In[30]:


def rental_rate_getter(tag):
    import re
    rates = tag.find_all('td', string = re.compile('Rental Rate'))

    rates.remove(rates[0])


    return [rate.next_sibling.next_sibling.find('li').text
            for rate in rates]


# In[31]:


#extracts the unique address of each listing
def listing_name_finder(tag):
    import re
    return tag.find(href = re.compile('www.loopnet.com/Listing')).get_text()
    
    


# In[32]:


#extracts the href from each listing.
def href_getter(tag):
    import re
    return tag.find(href = re.compile('www.loopnet.com/Listing'))['href']

    


# In[33]:


def num_spaces_list(tag, num_listings):
    
    listing_info = tag.find_all('ul', class_ = 'data-points')
    if len(listing_info) != num_listings:
        listing_info = tag.find_all('div', class_ = 'data')
    
    print(len(listing_info))
    num_spaces = []
    for info in listing_info:
        start_index = info.get_text().index('(')
        stop_index = info.get_text().index(')') + 1
        num_spaces.append(info.get_text()[start_index:stop_index].split(' ')[0][1:])
    return num_spaces


# In[34]:


#returns the number of pages for that city's listings. Will use this value for range of the outermost for loop
def get_largest_page_num(tag):
    page_nums = tag.find('ol', class_ = 'paging').get_text()
    dots = page_nums.find('...')
    if dots > 0:
        return int(page_nums[dots+3:])
    else:
        return int(page_nums[-1])


# In[35]:


def properties_table_maker(soup):
    properties = pd.DataFrame()
    property_names = []
    hrefs = []
    listings = soup.find_all('article')
    for listing in listings:
        property_names.append(listing_name_finder(listing))
        hrefs.append(href_getter(listing))
    
    #print('hrefs length is: ' + str(len(hrefs)))
    #print('property_names length is: ' + str(len(property_names)))
    #print(property_names)
    properties['Property Name'] = property_names
    properties['Listing URL'] = hrefs
    #print('num_spaces length is: ' + str(len(num_spaces_list(soup, len(property_names)))))
    #print(num_spaces_list(soup, len(property_names)))
    #properties["Number of Spaces"] = num_spaces_list(soup, len(property_names))
    return properties


# In[18]:


#city_input = input('Enter the city in california you wish to look up: ')


# In[19]:


#city = city_input.lower().replace(' ', '-')


# In[39]:


#This script uses all the functions to create a dataframe containing information about each 
#individual space in every office listing for the city of the user's choice in california.
def listings_scrape(city):
    city = city.lower().replace(' ', '-')
    url_one = 'http://www.loopnet.com/for-lease/' + city + '-ca/office/'
    #page_position = url_one.index('')
    try:
        page_one = requests.get(url_one)
        print(page_one)
        page_one_soup = BeautifulSoup(page_one.content, "html.parser")
        print(page_one_soup)


        spaces_list = []
        #pages iterator
        for i in range(1, get_largest_page_num(page_one_soup) + 1):
            if i == 1:
                url = url_one
            else:
                i_str = str(i)
                url = url_one + i_str + '/'
                #url = url_one[:page_position] + i_str + url_one[page_position:]
    
            page = requests.get(url)
            page_soup = BeautifulSoup(page.content, "html.parser")
            page_properties = properties_table_maker(page_soup)
    
            print(page_properties)
            #listings iterator
            for j in range(len(page_properties.index)):
                listing_url = page_properties.loc[j, 'Listing URL']
                listing_page = requests.get(listing_url)
                listing_soup = BeautifulSoup(listing_page.content, "html.parser")
                name_city_zip_list = name_city_zipcode(listing_soup)
                #print("the name_city_zip_list is: " + str(name_city_zip_list))
                property_type = property_type_getter(listing_soup)
                #print("The property type is: " + str(property_type))
                rentable_building_area = rentable_building_area_getter(listing_soup)
                #print("The rentable building area is " + str(rentable_building_area))
                num_spaces = num_spaces_getter(listing_soup)
                #print('number of spaces is: ' + str(num_spaces))
    
                listings_dict = dict([('Address', name_city_zip_list[0]),
                              ('City', name_city_zip_list[1]),
                              ('Zipcode', name_city_zip_list[2]), 
                              ('Property Type', property_type.strip()),
                              ('Rentable Building Area', rentable_building_area),
                              ('Number of Spaces', num_spaces)])
    
                rental_rates = rental_rate_getter(listing_soup)
                #print(rental_rates)
                service_types = service_types_getter(listing_soup)
                #print(service_types)
                spaces_sqft = spaces_sqft_getter(listing_soup)
                #print(spaces_sqft)
                #floors = floors_getter(listing_soup)
                #print(floors)
        
                listing_spaces_df  = pd.DataFrame(columns = ('Address', 'City', 'Zipcode', 'Property Type', 
                                       'Rentable Building Area', 'Rental Rate', 
                                       'Service Type', 'Space Available'))
                #spaces iterator
                for spaces_counter in range(num_spaces):
                    #print('\t Space #{}'.format(spaces_counter + 1))
                    #print('\t' + str(rental_rates[spaces_counter]))
                    space1 = [listings_dict['Address'], listings_dict['City'],
                         listings_dict['Zipcode'], listings_dict['Property Type'],
                         listings_dict['Rentable Building Area'], rental_rates[spaces_counter],
                         service_types[spaces_counter].strip(), spaces_sqft[spaces_counter]]
            
                    #print(space1)
                    spaces_list.append(space1)
                    #print('onto the next space!')
        
                #print('onto the next listing!')
            #print('onto the next page!')
            #spaces_df = pd.DataFrame(spaces_list, columns = ('Address', 'City', 'Zipcode', 'Property Type', 
            #                       'Rentable Building Area (SF)', 'Rental Rate', 
            #                       'Service Type', 'Space Available (SF)'))
            
        
        return spaces_list
            #return spaces_df.to_csv(city + '.csv')
        
    except Exception as e:
        print(e)
        return None
    


# In[116]:



#def floors_getter(tag):
#    import re
    
#    all_floor_list = tag.find_all('td', string = re.compile('Floor'))
#    print(all_floor_list)
#    floor_list = []
  
 #   for i in range(1, len(all_floor_list), 2):
 #       floor = all_floor_list[i].text[2:].split(sep = ' ')[0]
 #       floor_list.append(floor)
  
#    return floor_list

