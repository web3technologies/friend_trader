from rest_framework import serializers


class VolumeSerializer(serializers.Serializer):
    value = serializers.IntegerField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        period_field_name = [key for key in instance.keys() if key not in ["total_volume", "time"]][0]
        representation['time'] = instance[period_field_name]

        return representation