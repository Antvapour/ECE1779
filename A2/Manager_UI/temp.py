if average_load > max_threshold :
    add_instance_num = int(len(cpu_stats_1) * (increase_rate-1))
    # add instances
    for i in range(add_instance_num) :
        instances = ec2.create_instances(ImageId=config.ami_id, InstanceType='t2.small', MinCount=1, MaxCount=1,
                     Monitoring={'Enabled': True},
                     Placement={'AvailabilityZone': 'us-east-1a', 'GroupName': 'A2_workerpool'},
                     SecurityGroups=[
                         'launch-wizard-8',
                     ],
                     KeyName='ece1779_A2_user', TagSpecifications=[
                        {
                            'ResourceType': 'instance',
                            'Tags': [
                                {
                                    'Key': 'Name',
                                    'Value': 'Additional_workers'
                                },
                            ]
                        }, ])

    #resize ELB
    for instance in instances:
        client.register_instances_with_load_balancer(
                    LoadBalancerName='ece1779A2',
                    Instances=[Instances=[{'InstanceId': instance.id}])

    #wait until finish
    waiter = client.get_waiter('instance_in_service')
    waiter.wait(
                LoadBalancerName='ece1779A2',
                Instances=[{'InstanceId': instance.id}])


if average_load < min_threshold :
    minus_instance_num = int(len(cpu_stats_1) * (1-decrease_rate))

    if minus_instance_num > 0 :
        ids_to_delete = ids[:minus_instance_num]
        #resize ELB
        for id in ids_to_delete :
            client.deregister_instances_from_load_balancer(
                        LoadBalancerName='ece1779A2',
                        Instances=[Instances=[{'InstanceId': instance.id}])

        #wait until finish
        waiter = client.get_waiter('instance_deregistered')
        waiter.wait(
                    LoadBalancerName='ece1779A2',
                    Instances=[{'InstanceId': id}])

        # drop instances
        for id in ids_to_delete :
            ec2.instances.filter(InstanceIds=[id]).terminate()

    #wait for some time
