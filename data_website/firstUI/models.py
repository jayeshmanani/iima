from django.db import models
import datetime

# Create your models here.
class Country(models.Model):
    country_name = models.CharField(max_length=100, unique=True)
    country_id = models.CharField(max_length=10, unique=True)
    country_code = models.CharField(max_length=10, unique=True)
    default_hist = models.BooleanField(default=0)
    region = models.CharField(max_length=100)

    def __str__(self):
        return self.country_name


class FinanceData(models.Model):
    country_id = models.ForeignKey('Country', on_delete=models.CASCADE)
    data_year = models.IntegerField(default=(datetime.datetime.today().year)-1)
    fiscal_balance_gdp = models.FloatField(default=None, null=True, blank=True) 
    government_grossdebt_gdp = models.FloatField(default=None, null=True, blank=True) 
    inflation_data = models.FloatField(default=None, null=True, blank=True) 
    exports_growth = models.FloatField(default=None, null=True, blank=True) 
    savings_gdp = models.FloatField(default=None, null=True, blank=True) 
    externaldebt = models.FloatField(default=None, null=True, blank=True) 
    exports = models.FloatField(default=None, null=True, blank=True) 
    reserves = models.FloatField(default=None, null=True, blank=True) 
    real_gdppc = models.FloatField(default=None, null=True, blank=True) 
    imports = models.FloatField(default=None, null=True, blank=True) 
    real_gdpgrowth = models.FloatField(default=None, null=True, blank=True) 
    real_gnipc = models.FloatField(default=None, null=True, blank=True) 
    nominal_gdp = models.FloatField(default=None, null=True, blank=True) 
    political_stability = models.FloatField(default=None, null=True, blank=True) 
    rule_of_law = models.FloatField(default=None, null=True, blank=True) 
    govt_effectiveness = models.FloatField(default=None, null=True, blank=True) 
    m3_gdp = models.FloatField(default=None, null=True, blank=True) 
    externaldebt_exports = models.FloatField(default=None, null=True, blank=True) 
    reserves_import = models.FloatField(default=None, null=True, blank=True) 
    reserves_gdp = models.FloatField(default=None, null=True, blank=True) 
    log_real_gnipc = models.FloatField(default=None, null=True, blank=True) 
    predicted_specgrade = models.FloatField(default=None, null=True, blank=True) 
    Speculative_Grade_Prob = models.FloatField(default=None, null=True, blank=True) 
    y_hat = models.FloatField(default=None, null=True, blank=True) 
    Threshold_Yhat_sigma = models.FloatField(default=None, null=True, blank=True) 
    Debt_Distress_prob = models.FloatField(default=None, null=True, blank=True) 
    show = models.BooleanField(default=True)
    lastUpdate = models.DateField(auto_now=True)


    def __str__(self):
        return str(self.country_id)+' '+str(self.data_year)

    




