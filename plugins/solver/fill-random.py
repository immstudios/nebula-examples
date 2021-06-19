from nebula import *

class Plugin(SolverPlugin):
    def solve(self):
        self.db.query("""
                SELECT meta FROM assets
                WHERE
                    id_folder=5
                AND CAST(meta->>'qc/state' AS INTEGER) = 4
                AND status = 1

                ORDER BY RANDOM()
            """)

        for meta, in self.db.fetchall():
            if self.current_duration > min(self.placeholder.duration, self.needed_duration):
                """
                self.placeholder.duration :  a duration of the placeholder used for solving
                self.needed_duration      :  a "free space" in the current block
                                             (next_event_start - current_event_start - sum_of_existing_items_durs)
                                             if there is no following event, defalut duration 3600 s is used
                """
                return

            asset = Asset(meta=meta, db=self.db)
            yield Item(meta={
                    "id_asset" : asset.id,
                })

            yield Item(meta={
                    "id_asset" : 18849,
                })


