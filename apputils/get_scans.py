import haloscans
from multiprocessing.dummy import Pool as ThreadPool


class GetScans(object):
    def __init__(self, key, secret, batch_size, target_date):
        search_params = {"since": target_date, "sort_by": "created_at.asc"}
        self.h_s = haloscans.HaloScans(key, secret,
                                       search_params=search_params)
        self.enricher = haloscans.HaloScanDetails(key, secret)
        self.target_date = target_date
        self.batch_size = batch_size
        self.max_threads = 10
        print("Scan retrieval initialized for date %s") % self.target_date

    def __iter__(self):
        batch = []
        for scan in self.h_s:
            if scan["created_at"].startswith(self.target_date):
                batch.append(scan["id"])
                if len(batch) >= self.batch_size:
                    yield list(self.get_enriched_scans(batch))
                    batch = []
            else:
                yield list(self.get_enriched_scans(batch))
                print("No more scans for target day!")
                raise StopIteration

    def get_enriched_scans(self, scan_ids):
        """Magic happens here... we map pages to threads in a pool, return
        results when it's all done."""
        self.enricher.halo_session = self.enricher.build_halo_session()
        pool = ThreadPool(self.max_threads)
        results = pool.map(self.enricher.get, scan_ids)
        pool.close()
        pool.join()
        return results
