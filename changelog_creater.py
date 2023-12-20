
def changelog_activate(changelog, driver, WebDriverWait, EC, By):
    # get to the changelog site 
    driver.get("")
    # fill change log and loop throught the list then add the titles
    product_container = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "product")))
    driver.execute_script("arguments[0].scrollIntoView();", product_container)

    add_item_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "cx-ui-repeater-add")))
    for i in range(0, len(changelog)):
        if i == 0:
            driver.execute_script("arguments[0].click();", add_item_button)
            item = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, f"title-{i}")))
            driver.execute_script("arguments[0].scrollIntoView();", item)
            driver.execute_script("arguments[0].value = arguments[1];", item, changelog[i])
        else:
            # Print other items in the list
            driver.execute_script("arguments[0].click();", add_item_button)
            item = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, f"title-{i}")))
            driver.execute_script("arguments[0].scrollIntoView();", item)
            driver.execute_script("arguments[0].value = arguments[1];", item, changelog[i])

    publish = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "cx-button.cx-button-primary-style")))
    driver.execute_script("arguments[0].scrollIntoView();", publish)
    driver.execute_script("arguments[0].click();", publish)
