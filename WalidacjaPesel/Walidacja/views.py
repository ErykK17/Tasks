from django.views.generic import FormView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .forms import PeselForm


def get_gender(pesel):
    """Zwraca płeć na podstawie numeru PESEL."""
    return 'Kobieta' if int(pesel[9]) % 2 == 0 else 'Mężczyzna'


def get_birthday(pesel):
    """Zwraca datę urodzenia w formacie YYYY-MM-DD na podstawie numeru PESEL."""
    year_map = {0: '19', 8: '18', 2: '20', 4: '21', 6: '22'}
    year_prefix = year_map[int(pesel[2]) // 2]
    year = year_prefix + pesel[:2]
    month = str(int(pesel[2:4]) % 20).zfill(2)
    day = pesel[4:6]
    return f'{year}-{month}-{day}'


def validate_pesel(pesel):
    """Sprawdza długość PESEL oraz poprawność numeru kontrolnego."""
    if len(pesel) != 11 or not pesel.isdigit():
        return False, False, False

    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    checksum = sum(int(pesel[i]) * weights[i] for i in range(10))
    control_number_is_valid = (10 - (checksum % 10)) % 10 == int(pesel[10])
    birth_month_is_valid = int(pesel[2:4]) % 20 <= 12
    return True, control_number_is_valid, birth_month_is_valid


class PeselValidation(FormView):
    """Widok z formularzem do podania PESELU do sprawdzenia."""
    template_name = 'validate_pesel.html'
    form_class = PeselForm
    success_url = reverse_lazy('result')

    def form_valid(self, form):
        self.request.session['pesel'] = form.cleaned_data['pesel']
        return redirect('result')


class ResultView(TemplateView):
    """Widok wyświetlający wynik walidacji PESEL oraz pobrane informacje o osobie."""
    template_name = 'result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pesel = self.request.session.get('pesel')
        
        if pesel:
            length_valid, control_valid, birth_valid = validate_pesel(pesel)
            context.update({
                'pesel': pesel,
                'length': "Prawidłowa długość" if length_valid else "Nieprawidłowa długość",
                'control_number': "Numer kontrolny prawidłowy" if control_valid else "Nieprawidłowy numer kontrolny",
                'birth_month_valid': "Miesiąc urodzenia poprawny" if birth_valid else "Nieprawidłowy miesiąc urodzenia",
                'birthday': get_birthday(pesel) if length_valid else "Niepoprawna data",
                'gender': get_gender(pesel) if length_valid else "Nieznana płeć"
            })
        else:
            context['pesel'] = 'Brak peselu'
        
        return context
