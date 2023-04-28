class DB_S_Titorovskaya:
    route_app_lables ={'titorovka'}

    def db_for_read(self,model,**hints):
        if model._meta.app_label in self.route_app_lables:
            return 'titorovka_db'
        return None
    def db_for_write(self,model,**hints):
        if model._meta.app_label in self.route_app_lables:
            return 'titorovka_db'
        return None

    def allow_migrste(self,db,app_lable,model_name=None,**hints):
        if app_lable in self.route_app_lables:
            return db=='titorovka_db'
