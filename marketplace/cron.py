import kronos
from .models import SpecialOffer

@kronos.register("0 0 * * *")
def check_if_offer_has_ended():
    special_offers = SpecialOffer.objects.filter(is_finished=False)
    for special_offer in special_offers:
        if not special_offer.is_ongoing:
            special_offer.is_finished = True
            special_offer.save()
