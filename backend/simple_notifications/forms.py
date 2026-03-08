from django import forms

from simple_notifications.models import NotificationPreferences


class NotificationPreferencesForm(forms.ModelForm):
    class Meta:
        model = NotificationPreferences
        fields = [
            "notification_frequency",
            "quiet_hours_timezone",
            "quiet_hours_start",
            "quiet_hours_end",
        ]
        widgets = {
            "quiet_hours_start": forms.TimeInput(attrs={"type": "time"}),
            "quiet_hours_end": forms.TimeInput(attrs={"type": "time"}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("quiet_hours_start")
        end = cleaned.get("quiet_hours_end")
        if start and not end:
            raise forms.ValidationError("Quiet hours end is required when start is set.")
        if end and not start:
            raise forms.ValidationError("Quiet hours start is required when end is set.")
        return cleaned
