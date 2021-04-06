
We are using docker with a postgres db

If you are on linux, you will need to run the following command 
to give docker the permissions it needs

Run `sudo chown -R $USER:$USER .` from the project root

Then running ls -l should show that you have ownership over all the docker files

Then from the root run `docker-compose up`

