import math
import requests

attibutes = ('id', 'name', 'model', 'year', 'color', 'price', 'latitude', 'longitude')  

def count_distance(lt1, lg1, lt2, lg2):
    rad = 6372795

    lat1 = lt1*math.pi/180.
    lat2 = lt2*math.pi/180.
    long1 = lg1*math.pi/180.
    long2 = lg2*math.pi/180.

    cl1 = math.cos(lat1)
    cl2 = math.cos(lat2)
    sl1 = math.sin(lat1)
    sl2 = math.sin(lat2)
    delta = long2 - long1
    cdelta = math.cos(delta)
    sdelta = math.sin(delta)

    y = math.sqrt(math.pow(cl2*sdelta, 2)+ math.pow(cl1*sl2 - sl1*cl2*cdelta, 2))
    x = sl1*sl2 + cl1*cl2*cdelta
    ad = math.atan2(y, x)

    return ad*rad


class Vehicle:
    count = 0

    @classmethod
    def incr(self):
        self.count += 1
        return self.count
    
    def __init__(self, **data) -> None:
        try:
            for key, value in data.items():
                if key in attibutes:
                    setattr(self, key, value)

            if 'id' not in self.__dict__.keys():
                self.id = self.incr()

        except Exception as e:
            print(e)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.name} {self.model} {self.year} {self.color} {self.price}" 

class VehicleManager:
    def __init__(self, url) -> None:   
        self.url = url
        self.__vehicles = self.get_vehicles()

    def __repr__(self) -> str:
        return '\n'.join(str(x) for x in self.__vehicles)
    
    def get_vehicles(self) -> list[Vehicle]:      
        r = requests.get(f"{self.url}/vehicles")

        if r.status_code == 200:
            return [Vehicle(**item) for item in r.json()]
        else:
            self.get_vehicles()

    def filter_vehicles(self, params) -> list[Vehicle]:
        return [x for x in self.__vehicles if all(x.__dict__[key] == value for key, value in params.items())]

    def get_vehicle(self, vehicle_id) -> Vehicle:        
        r = requests.get(f"{self.url}/vehicles/{vehicle_id}")

        if r.status_code == 200:
            return [x for x in self.__vehicles if x.id == vehicle_id][0]
        else:
            raise Exception("Vehicle not found")

    def add_vehicle(self, vehicle) -> Vehicle:       
        if vehicle not in self.__vehicles:
            self.__vehicles.append(vehicle)
            r = requests.post(f"{self.url}/vehicles", json=vehicle.__dict__)
            
            return vehicle
        else:
            raise Exception("Vehicle already exists")

    def update_vehicle(self, vehicle) -> Vehicle:
        if vehicle not in self.__vehicles: 
            for ind, item in enumerate(self.__vehicles):
                if item.id == vehicle.id:
                    r = requests.put(f"{self.url}/vehicles/{vehicle.id}", json=vehicle.__dict__)   
                    self.__vehicles[ind] = vehicle
                    break

            return vehicle
        else:
            print("There is the same vehicle already exists")

    def delete_vehicle(self, id) -> None:     
        if id in [x.id for x in self.__vehicles]:
            self.__vehicles.remove([x for x in self.__vehicles if x.id == id][0])
            r = requests.delete(f"{self.url}/vehicles/{id}")
        else:
            raise Exception("Vehicle not found")

    def get_distance(self, id1, id2) -> float: 
        possible_ids = [x.id for x in self.__vehicles]
        if id1 in possible_ids and id2 in possible_ids:    
            vehicle_1 = self.get_vehicle(id1)
            vehicle_2 = self.get_vehicle(id2)
            res = count_distance(vehicle_1.latitude, vehicle_1.longitude, vehicle_2.latitude, vehicle_2.longitude)

            return res
        else:
            raise Exception("Id not found")
        
    def get_nearest_vehicle(self, id) -> Vehicle:
        if id in [x.id for x in self.__vehicles]:
            return min(self.__vehicles, key=lambda x: self.get_distance(id, x.id) if x.id != id else float('inf'))
        else:
            raise Exception("Id not found")


