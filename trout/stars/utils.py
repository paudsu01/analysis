from trout.database import query
from trout.nights import bad_nights

STAR_START = 1
STAR_END = 2510


def is_valid_star(star_number: int):
    return star_number >= STAR_START and star_number <= STAR_END


def star_table_name(star_number: int, is_primary: bool = True):
    # Only return if valid star_number provided
    if is_valid_star(star_number):
        if is_primary:
            return f"star_{star_number}_4px"
        else:
            return f"star_{star_number}_4px_exp"


def get_star_data(star_number: int, is_primary: bool):
    """
    Gives the stars data from the database for a particular star.
    This function filters out any bad nights in the data.
    param: star_number
    return: tuple of 3 tuple consisting (id, magnitude, date)
    """

    table = star_table_name(star_number, is_primary)

    if table:
        # Tuple used for enforcing immutability
        return bad_nights_filtered_data(
            tuple(query(f"SELECT * FROM {table}")), is_primary
        )


def bad_nights_filtered_data(data, is_primary: bool):
    """
    Returns the list of data points after filtering bad nights data in given
    data
    """
    # Using negative limit to ensure that all nights will be returned
    # Map used to remove the index and only keep the dates
    all_bad_nights = list(map(lambda x: x[1], bad_nights(-1, is_primary)))
    return list(filter(lambda x: x[2] not in all_bad_nights, data))
