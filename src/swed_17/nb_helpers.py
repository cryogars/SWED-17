from dask.distributed import Client, SSHCluster


def start_cluster(n_workers=10, memory_limit='4GB', local=True):
    if local:
        cluster = Client(
            n_workers=n_workers,
            threads_per_worker=1,
            memory_limit=memory_limit,
            dashboard_address=":8797",
        )
    else:
        # NOTE:
        # First host in the list is the scheduler, all others are workers
        ssh_cluster = SSHCluster(
            ["localhost", "honduras"],
            connect_options={
                "known_hosts": None,
            },
            worker_options={
                "nthreads": 1,
                "n_workers": n_workers,
                "memory_limit": memory_limit,
            },
            scheduler_options={
                "port": 0,
                "dashboard_address": ":8797"
            }
        )
        cluster = Client(ssh_cluster)

    print(cluster.dashboard_link)
    return cluster
