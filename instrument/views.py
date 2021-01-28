from django.shortcuts import render, redirect
from instrument.forms import *
from instrument.models import *
from django.http import JsonResponse


def instruments_main(request):

    print("====================")
    print("INSTRUMENT MAIN PAGE")
    print("====================")

    instrument_form = InstrumentForm()

    return render(request, 'instruments/instruments_main.html', {"instrument_form": instrument_form})


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


def get_instruments_url(request):
    print("*** GET INSTRUMENTS ***")

    print("Sending data to front end")

    response = {"message": "instruments"}

    return JsonResponse(response, safe=False)

