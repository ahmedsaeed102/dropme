import kronos
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template
from users_api.models import UserModel, LanguageChoices
from .utlis import get_user_logs, get_remaining_points


@kronos.register("0 8 * * 5")
def send_weekly_recycle_summary_email():
    from_email = f'DropMe <{settings.EMAIL_HOST_USER}>'

    for user in UserModel.objects.filter(is_active=True):
        data = get_user_logs(user.id)
        remaining_points = get_remaining_points(user)
        context = {"username": user.username, "rank":user.ranking, "remaining_points": remaining_points, "total_points": user.total_points}
        context.update(data)

        if data['recycled']:
            if user.preferred_language == LanguageChoices.ARABIC:
                subject = "تقدمك الأسبوعي في إعادة التدوير مع Drop Me 🌱"
                template = get_template("active_recylce_weekly_summary_arabic.html").render(context)
            else:
                subject = "Your Weekly Recycling Progress with Drop Me 🌱"
                template = get_template("active_recylce_weekly_summary_english.html").render(context)

        elif not data["recycled"]:
            if user.preferred_language == LanguageChoices.ARABIC:
                subject = "لنبدأ رحلتك في إعادة التدوير مع Drop Me 🌱"
                template = get_template("inactive_recylce_weekly_summary_arabic.html").render(context)
            else:
                subject = "Let's Get Started on Your Recycling Journey with Drop Me 🌱"
                template = get_template("inactive_recylce_weekly_summary_english.html").render(context)

        send_mail(subject, None, from_email, [user.email], fail_silently=False, html_message=template)
    print("Weekly Summary Emails Sent")

@kronos.register("30 10 * * *")
def send_app_email():
    from_email = f'DropMe <{settings.EMAIL_HOST_USER}>'
    context = {"testing_link": "https://play.google.com/apps/testing/com.dropme.recycling", "support_email": "hello@dropmeeg.com"}
    recipient_list = [
        "Abdoakram200014@gmail.com",
        "ahmedxd1359@gmail.com",
        "Prsuit24@gmail.com",
        "araby.kareem@gmail.com",
        "alcoach.net@gmail.com",
        "77wom77@gmail.com",
        "nourhanmassoud1@gmail.com",
        "asmaa.aborayia@gmail.com",
        "marwa.kershless@gmail.com",
        "Israa@lastconsultancy.com",
        "luckyahmed55@hotmail.com",
        "mohamednaeim59@gmail.com",
        "Khaledabbas.abbas@gmail.com",
        "mfatthy@gmail.com",
        "msaid2811@gmail.com",
        "belalsebaee23@gmail.com",
        "Hanimohamedacm2023@gmail.com",
        "hamed.id@gmail.com",
        "amirtad.b@gmail.com",
        "ahsaeed992@gmail.com",
        "as2173144@gmail.com",
        "tareksaeed476@gmail.com",
        "mohamed.osman7430@gmail.com",
        "a.allam858@gmail.com",
        "mmohie@viavr.solutions",
        "nourhanibrahim184@gmail.com",
        "Ayman.elafiefi@gmail.com",
        "abdallahwael421@gmail.com",
        "youssefgoda634@gmail.com",
        "Dahlia.moustafak@gmail.com",
        "FatmaAldahor@gmail.com",
        "aya.manaa.2002@gmail.com",
        "Elt2051@gmail.com",
        "mho23666@gmail.com",
        "omar.albltagy77@gmail.com",
        "aadelaly11@gmail.com",
        "t_r_osman@yahoo.com",
        "Srkhalil.7@gmail.com",
        "kirolos.melika@gmail.com",
        "rehamelfakharany770@gmail.com",
        "mzaki@loopeg.com",
        "Kareemelnagar18@gmail.com",
        "Sarahrushdy@gmail.com",
        "saelsheme@gmail.com",
        "lameesahmedvlogs@gmail.com",
        "suhailaahmedbk@gmail.com",
        "m.islam564321@gmail.com",
        "sosaahmed57@gmail.com",
        "sohaila.hussein00@eng-st.cu.edu.eg",
        "mohamed.hesham.7.mh7@gmail.com"
        "faresa.bakhit@gmail.com"
    ]
    subject = "Reminder: Keep Testing the Drop Me App!"
    template = get_template("download_app.html").render(context)
    send_mail(subject, None, from_email, recipient_list, fail_silently=False, html_message=template)