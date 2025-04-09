import csv


def wright_csv(file_name: str, res: str):
    print('csv=', res)
    with open(file_name, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'image_link', 'describe', 'state_tag', 'price', 'location_date', 'describe_link'])
        writer.writerows(res)
