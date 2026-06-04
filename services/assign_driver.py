from test_dummy_data import DELIVERIES,DRIVERS,WAREHOUSE
from collections import defaultdict
from geopy.distance import geodesic 

CLUSTER_DISTANCE=5
VAN_THRESHOLD=3

class DistanceCalculatorMixin:
    def calculate_distance(self,loc1,loc2):
        coord1=(loc1['location']['lat'],loc1['location']['lng'])
        coord2=(loc2['location']['lat'],loc2['location']['lng'])
        return geodesic(coord1,coord2).kilometers
    
    def calculate_distance_from_warehouse(self,loc,warehouse):
        coord1=(loc['location']['lat'],loc['location']['lng'])
        coord2=(warehouse['lat'],warehouse['lng'])
        return geodesic(coord1,coord2).kilometers
    
    def calculate_distances_from_warehouse(self,deliveries,warehouse):
        distances=[]
        for delivery in deliveries:
            delivery_coord=(delivery['location']['lat'],delivery['location']['lng'])
            warehouse_coord=(warehouse['lat'],warehouse['lng'])
            distances.append(geodesic(delivery_coord,warehouse_coord).kilometers)
        return distances
    
    def build_clusters(self,deliveries):
        unvisited=deliveries.copy()
        clusters=[]

        # while there is a delivery, go on
        while unvisited:
            # I'm picking the last delivery to start building clusters
            seed=unvisited.pop()
            cluster=[seed]
            stack=[seed]

            while stack:
                current=stack.pop()
                for delivery in unvisited:
                    if self.calculate_distance(current,delivery)<CLUSTER_DISTANCE and len(cluster)<=VAN_THRESHOLD:
                        cluster.append(delivery)
                        stack.append(delivery)
                        unvisited.remove(delivery)
            clusters.append(cluster)
        return clusters
    def clcluate_max_distance(self,cluster,warehouse):
        return max(self.calculate_distances_from_warehouse(cluster,warehouse))
    def calculate_average_distance(self,cluster,warehouse):
        return sum(self.calculate_distances_from_warehouse(cluster,warehouse))//len(self.calculate_distances_from_warehouse(cluster,warehouse))
    def score_cluster(self, cluster):
        weights = {'critical': 100, 'high': 10, 'normal': 1}
        return sum(weights.get(d['priority'], 0) for d in cluster)

class DeliveryFilterMixin:
    def filter_temp_sensitive(self,deliveries):
        temp=[d for d in deliveries if d['temperature_sensitive']]
        return temp
    
    def filter_regular(self,deliveries):
        regular=[d for d in deliveries if not d['temperature_sensitive']]
        return regular
    
    def filter_by_priority(self, deliveries):
        # TODO: Separate deliveries by priority (hospital > clinic > pharmacy)
        # 1. get the regular, non-temp-sensitive deliveries
        non_temp_sensitives=self.filter_regular(deliveries)
        critical=[delivery for delivery in non_temp_sensitives if delivery['priority']=='critical']
        high=[delivery for delivery in non_temp_sensitives if delivery['priority']=='high']
        normal=[delivery for delivery in non_temp_sensitives if delivery['priority']=='normal']

        return critical,high,normal

class AssignDeliveriesService(DeliveryFilterMixin,DistanceCalculatorMixin):
    def __init__(self, deliveries=DELIVERIES, drivers=DRIVERS, warehouse=WAREHOUSE):
        self.deliveries = deliveries
        self.drivers = drivers
        self.warehouse = warehouse
        self.assignments=self.assign_all()
    def __repr__(self):
        lines = []
        for deliveries in self.assignments.items():
            for delivery in deliveries:
                lines.append(f"To {delivery['destination_type']} Temp_sensitive: {delivery['temperature_sensitive']}")
        return "\n".join(lines)

    def get_refrigerated_driver(self):
        # TODO: Find and return the driver with refrigerated van
        return next(driver for driver in self.drivers if driver['van_type']=='refrigerated')

    def get_large_van_drivers(self):
        return [driver for driver in self.drivers if driver['van_type']=='big']

    def get_small_van_drivers(self):
        return [driver for driver in self.drivers if driver['van_type']=='small']
    
    def assign_all(self):
        # TODO: Main method - orchestrate all assignment steps
        assignments=defaultdict(list)
        # 1.Get the refrigrated van driver
        refrigrated_driver=self.get_refrigerated_driver()
        # 2. get the temp sensitive ones
        temp=self.filter_temp_sensitive(self.deliveries)
        # 3.assign temperature sensitive deliveries
        for delivery in temp:
            assignments[refrigrated_driver['id']].append(delivery['id'])
        # I decided for a hybrid approach to combine distance and priority:
        # 1. building clusters and label them as short_distance or long
        regular=self.filter_regular(self.deliveries)
        clusters=self.build_clusters(regular)
        long_distance_deliveries=[]
        short_distance_deliveries=[]
        for cluster in clusters:
            max_distance=self.clcluate_max_distance(cluster,self.warehouse)
            avergae_distance=self.calculate_average_distance(cluster,self.warehouse)
            if avergae_distance<=8 and max_distance<=15:
                short_distance_deliveries.append(cluster)
            else:
                long_distance_deliveries.append(cluster) 
        # 2. Sort clusters based on priority
        long_distance_deliveries.sort(key=lambda c: self.score_cluster(c), reverse=True)
        short_distance_deliveries.sort(key=lambda c: self.score_cluster(c), reverse=True)            
        # 3. Assign drivers 
        big_drivers = self.get_large_van_drivers()
        small_drivers = self.get_small_van_drivers()
        
        for i, cluster in enumerate(long_distance_deliveries):
            driver = big_drivers[i % len(big_drivers)]
            for delivery in cluster:
                assignments[driver['id']].append(delivery['id'])

        for i, cluster in enumerate(short_distance_deliveries):
            driver = small_drivers[i % len(small_drivers)]
            for delivery in cluster:
                assignments[driver['id']].append(delivery['id'])

        return assignments

if __name__=='__main__':
    service=AssignDeliveriesService()
    print(service.assign_all())