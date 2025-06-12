import csv


def write_csv(file_name: str, res: list):
    with open(file_name, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'image_link', 'describe', 'state_tag', 'price', 'location_date', 'describe_link'])
        writer.writerows(res)
