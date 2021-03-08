#!/usr/bin/env bash

cleanup_files() {
  rm -rf /vagrant/sites
  dos2unix /vagrant/sites.conf
  dos2unix /vagrant/credentials.conf
}

copy_ssh_keys() {
  #Setup ids for cloning repos
  echo "Copy SSH keys..."
  cp /vagrant/keys/* ~/.ssh/.
  chmod 600 ~/.ssh/id_rsa
  echo "Copied"
}

copy_drushrc() {
  cp /vagrant/drushrc.php ~/.drush/.
}

clone_sites_all() {
  cd /etc/drupal/7/sites
  git clone #[REDACTED]
  cd all/themes
  git clone #[REDACTED]
  git clone #[REDACTED]
}

setup_drupal_files_to_exist_in_shared_folder() {
  mv /etc/drupal/7/sites /vagrant/sites
  ln -s -T /vagrant/sites /etc/drupal/7/sites

  #add www-data to vagrant group so server can read conf files
  adduser www-data vagrant
  adduser vagrant www-data
  service apache2 restart
}

provision_sites() {
  readarray -t -s2 sites < /vagrant/sites.conf
  number_of_sites=${#sites[@]}
  if [ "$number_of_sites" -gt 0 ]; then
    echo "Attempting to provision $number_of_sites site(s)"
    mkdir /var/lib/drupal7/private
    echo "Mount share"
    username_line=$(head -n 1 /vagrant/credentials.conf)
    username=${username_line#"username="}
    echo "Using username $username"
    temp_d7_share=`mktemp -d`
    mount -t cifs #[REDACTED]/$username $temp_d7_share -o credentials="/vagrant/credentials.conf"
    cd /vagrant/sites
    let i=0
    while (( number_of_sites > i)); do
      current_site="${sites[i++]}"
      provision_sites_clone $current_site
      provision_sites_files $current_site
      provision_sites_db $current_site
      clear_caches $current_site
    done
    chown -R www-data:www-data /var/lib/drupal7/private
    echo "Unmount share and remove dir"
    umount $temp_d7_share
    rmdir $temp_d7_share
    echo "Sites provisioned"
  else
    echo "No sites to provision."
  fi
}

provision_sites_clone() {
  echo "Attempting to clone $1"
  git clone #[REDACTED]
  echo "Cloned"
}

provision_sites_files() {
  echo "Attempting to copy files for $1"
  cp -R $temp_d7_share/$1/files /var/lib/drupal7/files/$1
  ln -s /var/lib/drupal7/files/$1 $1/files
  chown vagrant:vagrant $1/files
  chown -R www-data:www-data /var/lib/drupal7/files/$1
  mkdir /var/lib/drupal7/private/$1
  echo "Files copied"
}

provision_sites_db() {
  get_dbdump_from_drupal7 $1
  populate_mysql_db_from_dump $1
  create_settings_file_for_site $1
}

get_dbdump_from_drupal7() {
    #[REDACTED]
}

populate_mysql_db_from_dump() {
  safe_site_name=`echo $1 | tr '.' '_'`
  mysql -uroot -pvagrant -e "create database [REDACTED]_$safe_site_name;"
  mysql -uroot -pvagrant ltsmulti_$safe_site_name < dump.sql
  rm dump.sql
}

create_settings_file_for_site() {
  safe_site_name=`echo $1 | tr '.' '_'`
  cp /vagrant/sites/default/settings.php /vagrant/sites/$1/settings.php
  cp /vagrant/sites/default/dbconfig.php /vagrant/sites/$1/dbconfig.php
  sed -i "21s/drupal7/REDACTED_$safe_site_name/" /vagrant/sites/$1/dbconfig.php
  sed -i '22s/drupal7/root/' /vagrant/sites/$1/dbconfig.php
  sed -i "23s/.*/\'password\' =\> \'vagrant\'\,/" /vagrant/sites/$1/dbconfig.php
}

clear_caches() {
  cd /vagrant/sites/$1
  drush cc all
  cd /vagrant/sites
}


cleanup_files
copy_ssh_keys
copy_drushrc
clone_sites_all
setup_drupal_files_to_exist_in_shared_folder
provision_sites
