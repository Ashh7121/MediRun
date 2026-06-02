from test_dummy_data import DELIVERIES,DRIVERS,WAREHOUSE
from collections import defaultdict

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

class AssignDeliveriesService(DeliveryFilterMixin):
    def __init__(self, deliveries=DELIVERIES, drivers=DRIVERS, warehouse=WAREHOUSE):
        self.deliveries = deliveries
        self.drivers = drivers
        self.warehouse = warehouse
        self.filtered = DeliveryFilterMixin()
        self.assignments=self.assign_all()
    def __repr__(self):
        for driver_id, deliveries in self.assignments.items():
            for delivery in deliveries:
                print(f"To {delivery['destination_type']} Temp_sensitive: {delivery['temperature_sensitive']}")
                
    def get_refrigerated_driver(self):
        # TODO: Find and return the driver with refrigerated van
        return next(driver['id'] for driver in self.drivers if driver['van_type']=='refrigerated')

    def get_other_drivers(self):
        return [driver for driver in self.drivers if not driver['van_type']=='refrigrated']
    
    def assign_all(self):
        # TODO: Main method - orchestrate all assignment steps
        assignments=defaultdict(list)
        # 1.Get the refrigrated van driver
        refrigrated_driver=self.get_refrigerated_driver()
        # 2. from the filtered instance, get the temp sensitive ones
        temp=self.filtered.filter_temp_sensitive(self.deliveries)
        # 3.assign temperature sensitive deliveries
        for delivery in temp:
            assignments[refrigrated_driver].append(delivery)
        
        # Now by priority
        # 1. Get other drivers
        drivers=self.get_other_drivers()
        # 2. Get remaining deliveries that are not temperature sensitive
        regular=self.filtered.filter_regular(self.deliveries)
        # 3. From these deliveries, separate by priority
        critical,high,normal=self.filtered.filter_by_priority(regular)
        # 4. Now, we distribute between drivers
        regular_sorted=critical+high+normal
        for index,delivery in enumerate(regular_sorted):
            driver_index=index%len(drivers)
            assignments[driver_index].append(delivery)
        return assignments

if __name__=='__main__':
    service=AssignDeliveriesService()
    print(service)