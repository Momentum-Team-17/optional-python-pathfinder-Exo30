import sys 
import argparse
from PIL import Image
from PIL import ImageColor

parser = argparse.ArgumentParser()
parser.add_argument("-e", "--data", help="txt file with elevation data")
parser.add_argument("-pc", "--path_color", help="Optional variable for customizing path color")
parser.add_argument("-opc", "--optimal_path_color", help="Optional variable for customizing the optimal path color")
parser.add_argument("-lpc", "--lowest_path_color", help="Optional variable for customizing lowest path color")
args = parser.parse_args()
if args.optimal_path_color:
    optimal_color = args.optimal_path_color
else:
    optimal_color = None
if args.path_color:
    path_color = args.path_color
else:
    path_color = None
if args.lowest_path_color:
    lowest_path_color = args.lowest_path_color
else:
    lowest_path_color = None
filename = args.data

def open_file(filename):
    doc = open(filename, "r")
    return doc.read()


def map_creator(doc):
    coordinates = doc.split("\n")
    y_coordinates = []
    for x in coordinates:
        var = x.split(" ")
        y_coordinates.append(var)
    y_coordinates_length = len(y_coordinates[0]) 
    x_coordinates_length = len(y_coordinates)
    #print(y_coordinates_length, x_coordinates_length)
    map = Image.new("RGBA", (y_coordinates_length, x_coordinates_length), 'black')
    current_y_coor = 0
    current_x_coor = 0
    for y in y_coordinates:
        filtered = list(filter(lambda x: x != "", y))
        
        for x in filtered:
            if(x != ''):
                x = int(x)
                if x < 3500:
                    map.putpixel((current_x_coor, current_y_coor), (255, 255, 255, 255))
                if x >= 3500 and x < 3750:
                    map.putpixel((current_x_coor, current_y_coor), (224, 224, 224, 255))
                if x >= 3750 and x < 4000:
                    map.putpixel((current_x_coor, current_y_coor), (196, 196, 196, 255))
                if x >= 4000 and x < 4250:
                    map.putpixel((current_x_coor, current_y_coor), (168, 168, 168, 255))
                if x >= 4250 and x < 4500:
                    map.putpixel((current_x_coor, current_y_coor), (168, 168, 168, 255))
                if x >= 4500 and x < 4750:
                    map.putpixel((current_x_coor, current_y_coor), (140, 140, 140, 255))
                if x >= 4750 and x < 5000:
                    map.putpixel((current_x_coor, current_y_coor), (112, 112, 112, 255))
                if x >= 5000 and x < 5250:
                    map.putpixel((current_x_coor, current_y_coor), (84, 84, 84, 255))            
                if x >= 5250 and x < 5500:
                    map.putpixel((current_x_coor, current_y_coor), (56, 56, 56, 255))                
                if x >= 5500:
                    map.putpixel((current_x_coor, current_y_coor), (28, 28, 28, 255))            
                current_x_coor += 1
        current_y_coor += 1
        current_x_coor = 0
    map.save("newmap.png")

def map_paths(doc):
    map = Image.open('newmap.png')
    coordinates = doc.split("\n")
    y_coordinates = list(filter(lambda x : x != '' and x != " ", coordinates))
    y_coordinates = []
    for x in coordinates:
        var = x.split(" ")
        y_coordinates.append(var)
    y_coordinates_length = len(y_coordinates) 
    x_coordinates_length = len(y_coordinates[0])
    ystart = 0
    path_storage = []
    while ystart < y_coordinates_length - 1:
        paths = {}
        altitudes = []
        total_alt_change = 0
        path = []

        xposition = 0
        yposition = ystart        
        path.append((xposition, yposition))
        if path_color is not None:
            map.putpixel((xposition, yposition), ImageColor.getcolor(path_color, 'RGBA'))
        else:
            map.putpixel((xposition, yposition), (255, 0, 0, 255))

        while xposition < x_coordinates_length - 1:
            altitude = int(y_coordinates[yposition][xposition])
            option1 = None
            option3 = None
            if (yposition - 1 >= 0):
                option1 = int(y_coordinates[yposition - 1][xposition + 1])
                option1diff = option1 - altitude
            option2 = int(y_coordinates[yposition][xposition + 1])
            option2diff = option2 - altitude
            if (yposition + 1 <= y_coordinates_length - 2):
                option3 = int(y_coordinates[yposition + 1][xposition + 1])
                option3diff = option3 - altitude
            if(option2diff < 0):
                option2diff *= -1
            best_path = 2
            best_path_diff = option2diff
            if(option1 is not None):
                if(option1diff < 0):
                    option1diff *= -1
                if(option1diff < best_path_diff):
                    best_path = 1
                    best_path_diff = option1diff
            if(option3 is not None):
                if(option3diff < 0):
                    option3diff *= -1
                if(option3diff < best_path_diff):
                    best_path = 3
                    best_path_diff = option3diff 
            if (best_path == 1):
                yposition -= 1
            if (best_path == 3):
                yposition += 1
            xposition += 1 
            total_alt_change += best_path_diff
            path.append((xposition, yposition))
            altitudes.append(best_path_diff)
            if path_color is not None:
                map.putpixel((xposition, yposition), ImageColor.getcolor(path_color, 'RGBA'))
            else:
                map.putpixel((xposition, yposition), (255, 0, 0, 255)) 
        paths = {'total_alt_change': total_alt_change, 'path': path, 'altitude': altitudes}
        path_storage.append(paths)
        ystart += 1
    map.save("newmap_paths.png")
    return(path_storage)

def map_optimize(paths):
    map = Image.open('newmap_paths.png')
    optimal_path_map = Image.open('newmap.png')

    optimal_path_alt= paths[0]['total_alt_change']
    optimal_path = paths[0]['path']
    optimal_altitudes = paths[0]['altitude']
    count = 0
    upcount = 0
    for path in paths:
        if (path['total_alt_change'] < optimal_path_alt):
            optimal_path_alt = path['total_alt_change']
            optimal_path = path['path']
            optimal_altitudes = path['altitude']
    while count < len(optimal_path):
        coor = optimal_path[count]
        if optimal_color is not None:
            map.putpixel((coor[0], coor[1]), ImageColor.getcolor(optimal_color, 'RGBA'))
            optimal_path_map.putpixel((coor[0], coor[1]), ImageColor.getcolor(optimal_color, 'RGBA'))
        else:
            map.putpixel((coor[0], coor[1]), (0, 255, 0, 255))
            optimal_path_map.putpixel((coor[0], coor[1]), (0, 255, 0, 255))
        if count > 0 and count < len(optimal_path) -1:
            if optimal_altitudes[count] > optimal_altitudes[count - 1]:
                upcount += 1
                if upcount > 0:
                    if optimal_color != 'red' or optimal_color != 'pink':
                        optimal_path_map.putpixel((coor[0], coor[1]), ImageColor.getcolor('red', 'RGBA'))
                    else:
                        optimal_path_map.putpixel((coor[0], coor[1]), ImageColor.getcolor('blue', 'RGBA'))
            else:
                upcount = 0
            
        count += 1
    map.save('newmap_paths.png')
    optimal_path_map.save('optimal_path_map.png')

def map_lowest_path(doc):
    map = Image.open('newmap_paths.png')
    lowest_path_map = Image.open('newmap.png')

    coordinates = doc.split("\n")
    y_coordinates = list(filter(lambda x : x != '' and x != " ", coordinates))
    y_coordinates = []
    for x in coordinates:
        var = x.split(" ")
        y_coordinates.append(var)
    y_coordinates_length = len(y_coordinates) 
    x_coordinates_length = len(y_coordinates[0])

    xposition = 0
    yposition = 0
    count = 0
    start_alt = int(y_coordinates[0][0])
    
    while count < len(y_coordinates):
        if y_coordinates[count][0] != '':
            if int(y_coordinates[count][0]) < start_alt:
                start_alt = int(y_coordinates[count][0])
                yposition = count
        count += 1

    if lowest_path_color is not None:
        map.putpixel((xposition, yposition), ImageColor.getcolor(lowest_path_color, 'RGBA'))
        lowest_path_map.putpixel((xposition, yposition), ImageColor.getcolor(lowest_path_color, 'RGBA'))
    else:
        map.putpixel((xposition, yposition), ImageColor.getcolor('blue', 'RGBA'))
        lowest_path_map.putpixel((xposition, yposition), ImageColor.getcolor('blue', 'RGBA'))

    while xposition < x_coordinates_length - 1:
        altitude = int(y_coordinates[yposition][xposition])
        option1 = None
        option3 = None
        if (yposition - 1 >= 0):
            option1 = int(y_coordinates[yposition - 1][xposition + 1])
            option1diff = option1 - altitude
        option2 = int(y_coordinates[yposition][xposition + 1])
        option2diff = option2 - altitude
        if (yposition + 1 <= y_coordinates_length - 2):
            option3 = int(y_coordinates[yposition + 1][xposition + 1])
            option3diff = option3 - altitude
        best_path = 2
        best_path_diff = option2diff
        if(option1 is not None):
            if(option1diff < best_path_diff):
                best_path = 1
                best_path_diff = option1diff
        if(option3 is not None):
            if(option3diff < best_path_diff):
                best_path = 3
                best_path_diff = option3diff 
        if (best_path == 1):
            yposition -= 1
        if (best_path == 3):
            yposition += 1
        xposition += 1 

        if lowest_path_color is not None:
            map.putpixel((xposition, yposition), ImageColor.getcolor(lowest_path_color, 'RGBA'))
            lowest_path_map.putpixel((xposition, yposition), ImageColor.getcolor(lowest_path_color, 'RGBA'))
        else:
            map.putpixel((xposition, yposition), ImageColor.getcolor('blue', 'RGBA'))
            lowest_path_map.putpixel((xposition, yposition), ImageColor.getcolor('blue', 'RGBA'))
    map.save("newmap_paths.png")
    lowest_path_map.save('lowest_path_map.png')

def map_init(filename):
    doc = open_file(filename)
    map_creator(doc)
    paths = map_paths(doc)
    map_lowest_path(doc)
    map_optimize(paths)
    print("complete")



map_init(filename)
#filename = sys.argv[1]
#if __name__ == "__main__":
    #map_init(filename)