from django.shortcuts import render, redirect
from instrument.forms import *
from instrument.models import *
from django.http import JsonResponse


def new_instrument(request):
    print("==============")
    print("NEW INSTRUMENT")
    print("==============")

    if request.method == "POST":
        instrument_form = InstrumentForm(request.POST)

        if instrument_form.is_valid():
            instrument_name = instrument_form.cleaned_data["instrument_name"]
            instrument_type = instrument_form.cleaned_data["instrument_type"]
            source = instrument_form.cleaned_data["broker"]

            print("INSTRUMENT NAME:", instrument_name)
            print("INSTRUMENT TYPE:", instrument_type)

            print("SOURCE:", source)

            print("Saving new instrument to database")

            Instruments(instrument_name=instrument_name,
                        instrument_type=instrument_type,
                        source=source).save()

            print("New instrument was saved successfully")

        return redirect('instruments main')


def get_instruments(request):
    print("*** GET INSTRUMENTS ***")

    if request.method == "GET":

        broker = request.GET.get('broker')
        inst_type = request.GET.get('type')

        print('BROKER:', broker)
        print('INSTRUMENT TYPE:', inst_type)

        if broker is None:
            pass
        else:
            if broker == 'all':
                instruments = Instruments.objects.filter().values()
            else:
                instruments = Instruments.objects.filter(source=broker).values()

        if inst_type is None:
            pass
        else:
            instruments = Instruments.objects.filter(instrument_type=inst_type).values()

    print("Sending data to front end")

    response = list(instruments)

    return JsonResponse(response, safe=False)

