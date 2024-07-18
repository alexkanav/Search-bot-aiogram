import csv


def wright_csv(res):
    print('csv=', res)
    with open('olx_orders4.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'image_link', 'describe', 'state_tag', 'price', 'location_date', 'describe_link'])
        writer.writerows(res)
