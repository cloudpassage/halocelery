import haloevents


class GetEvents(object):
    def __init__(self, key, secret, batch_size, target_date):
        self.h_e = haloevents.HaloEvents(key, secret,
                                         start_timestamp=target_date)
        self.target_date = target_date
        self.batch_size = batch_size
        print("Event retrieval initialized for date %s") % self.target_date

    def __iter__(self):
        batch = []
        for event in self.h_e:
            if event["created_at"].startswith(self.target_date):
                if len(batch) >= self.batch_size:
                    yield list(batch)
                    batch = []
                else:
                    batch.append(event)
            else:
                yield list(batch)
                print("No more events for target day!")
                raise StopIteration
