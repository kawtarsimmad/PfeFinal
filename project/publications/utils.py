def get_funding_statistics(publications):
        #publications = cls.objects.all()
        total_funding_needed = sum(pub.montant for pub in publications)
        total_funding_collected = sum(pub.calculate_total_dons() for pub in publications)
        number_of_publications = publications.count()
        number_of_funded_publications = sum(1 for pub in publications if pub.calculate_total_dons() >= pub.montant)

        if total_funding_needed > 0:
            funding_percentage = (total_funding_collected / total_funding_needed) * 100
        else:
            funding_percentage = 0

        return {
            'total_funding_needed': total_funding_needed,
            'total_funding_collected': total_funding_collected,
            'number_of_publications': number_of_publications,
            'number_of_funded_publications': number_of_funded_publications,
            'funding_percentage': funding_percentage,
        }
