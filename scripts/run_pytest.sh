msrun --worker_num=8 --local_worker_num=8 --master_port=8118 --log_dir=msrun_log --join=True --cluster_time_out=300 pytest -vs tests/unit_tests/dist_checkpointing/test_optimizer.py::TestDistributedOptimizer

mpirun -n 8 pytest -vs tests/unit_tests/dist_checkpointing/test_optimizer.py::TestDistributedOptimizer