from royalroadlapi import *

fiction = get_fiction_object(17364)
data = get_fiction_info(fiction)

get_fictions("11343","11343",directory="Fiction - Epubs/")

print(get_fiction_location("8894",directory="Fiction - Epubs/"))
print(get_fiction_location("8894",directory="Fiction - Epubs/",start_chapter="1",end_chapter="5"))

get_fiction("8894",directory="Fiction - Epubs/")
get_fiction("8894",directory="Fiction - Epubs/",start_chapter="1",end_chapter="5")
get_fiction("8894",directory="Fiction - Epubs/",start_chapter="5",end_chapter="5")
get_fiction("8894",directory="Fiction - Epubs/",start_chapter="307",end_chapter="307")
get_fiction("8894",directory="Fiction - Epubs/",start_chapter="1",end_chapter="1")
get_fiction("8894",directory="Fiction - Epubs/",start_chapter="2",end_chapter="5")
get_fiction("8894",directory="Fiction - Epubs/",start_chapter="3",end_chapter="900")
get_fiction("8894",directory="Fiction - Epubs/",start_chapter="3")
get_fiction("8894",directory="Fiction - Epubs/",end_chapter="3")
get_fiction("8894",directory="Fiction - Epubs/",start_chapter="800",end_chapter="900")
get_fiction("8894",directory="Fiction - Epubs/",start_chapter="-20",end_chapter="900")

